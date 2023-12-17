## 1. naming rules
- class and object
	- camel： `class InstructionQueue()`, `instructionQueue = InstructionQueue() ` 
	- only `ReservationStations` and `ProcessingUnits` use plural form
	- `ReorderBuffer` instead of `ReOrderBuffer`
- methods
	- Logics inside an object is arbitrary
	- An object should expose the methods related to communication and different execution phases: e.g. `instructionQuque.issue()`
	- for simple communications, we just use the execution phase, e.g. `instructionQuque.issue()` & `instructionQuque.fetch()`
	- for objects need multiple steps to communicate(e.g. check availability), use `<phase>_<operation>`, e.g. `reorderBuffer.issue_check()` & `reorderBuffer.issue_write()`
	- for peripheral objects like memory, we just use `read()` and `write()`

## 2. overall structure
### objects:
#### Phase1:
```python
### 
class InstructionMemory:
class InstructionQueue: #<-- here keeps the pc
class ReorderBuffer:
class RegisterAliasTable:
class ArchitecturalRegisterFile:
class ReservationStations:
class ProcessingUnits:
class CommonDataBus:
### 
class InstructionStatusTable:

```
### runtime
- load configurations as a `json` file
- Init all components
- directly use a for loop to run the whole program
- the execution phases will be driven by functions taking different components as parameters
	- e.g. `def fetch(instructionMemory, instructionQueue)`

## 3. Execution phases & interfaces
#### the instruction
```python
class Instruction
### properties
	self.type #type of the instr(ADD,SUB..)
	self.operand1 #operand of this instr: number:1,2.5 ; str: 'R5', 'F3'
	self.operand2
	self.operand3 #will be the offset or pc target of Mem and Branch instrs
	self.issue #history of this instr, using cycle number 
	self.execute
	self.Memory
	self.writeBack
	self.commit
### methods
	def __init__(self,o_type,operand1,operand2,operand3):
	#the init fuction

```
#### fetch
```python
def fetch(instructionMemory, instructionQueue):
	instr = instructionMemory.read(instructionQueue.pc) #pc:int
	instructionQueue.fetch(instr)
```

#### issue
```python
def issue(instructionQueue, reorderBuffer, registerAliasTable,architecturalRegisterFile, reservationStations):
	#####
	##check availiability
	availiable = true
	availiable = availiable && instructionQueue.check_empty()
	availiable = availiable && !reorderBuffer.check_full()
	instr = instructionQueue.issue_touch()
	availiable = availiable && !reservationStations.check_full(instr)
	if(! availiable):
		return
	#####
	##get the instr
	instr = instructionQueue.issue_pop()# modify instr.issue
	rob_name = reorderBuffer.issue_push(instr) #rob_name should be "ROB<i>" like "ROB3"
	registerAliasTable.rename(instr.operand1, rob_name)
	"""
	ROB: 'ROB<i>'|value...
	RAT: 'R<i>'/'F<i>'|'R<i>'/'F<i>'/'ROB<i>'
	ARF: 'R<i>'/'F<i>'| value
	"""
	#####
	##renaming
	if(! isinstance(instr.operand2, str)):#immediate number
		operand2 = instr.operand2
	else:
		operand2 = registerAliasTable.get_alias(instr.operand2)
		if("ROB" in operand2):
			operand2 = reorderBuffer.get_value(operand2)
		else:
			operand2 = architecturalRegisterFile.get_value(operand2)

	### operand3 is the same
	#####
	##write in to RS
	reservationStations.issue_push(instr, operand2, operand3)
```

#### execution
```python
def execution(reservationStations, processingUnits)
	for i_type in reservationStations.type_list:# i_type = "int_add""float_add""float_multi"
		if(!reservationStations.check_ready(i_type))
			return
		if(processingUnits.check_full(i_type))
			return
		instr, operand1, operand2, operand3 = reservationStations.execution_pop()# modify instr.execute
		processingUnits.execution_push(instr, operand1, operand2, operand3)

	processingUnits.execution_run()
		
```

#### memory
```python
"""
not included in version1
"""
```

#### writeback
```python
def writeback(processingUnits, commonDataBus, reorderBuffer, reservationStations):
	###arbiter will try to find the instr with smallest issue cycle
	"""
	i_type = null
	pu = null
	idx = null
	instr = Null
	
		for pu in ProcessingUnits.pu_list:
			for candidate in pu.buffer:
				if candidate.issue < instr.issue 
					i_type = i_type
					pu = pu
					idx = idx
					instr = copy.deepcopy(candidate)
	"""
	instr,rob_name,value = get_instr_from_arbiter()
	
	reorderBuffer.writeback(instr,rob_name,value)
	reservationStations.writeback(rob_name,value)
```

#### commit
```python
def commit(reorderBuffer,registerAliasTable,architecturalRegisterFile,InstructionStatusTable):
	if (!reorderBuffer.check_ready())
		return
	reg_name, rob_name, instr,value = reorderBuffer.commit()
	registerAliasTable.commit(reg_name, rob_name, value)
	architecturalRegisterFile.commit(reg_name, value)
	InstructionStatusTable.commit(Instr)
```
