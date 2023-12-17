# Memory Queue

## 1. memory queue in different stages
#### 1. Fetch 
\< No Operations>
#### 2. issue
1. check instrQueue: no change
2. check ROB: no change
3. check RS: changes
	- if "Ld/Sd", check instr queue instead of RS
4. we should branch all out of the traditional path
	- i.e: check ROB --> if not Ld/Sd, ....
								 - >branch if Ld/Sd
5. Rename:
	- Ld Rx, n(Ry): rename rx in RAT, solve the dependency of Ry
	- Sd Rx, n(Ry): solve the dependency of both Rx and Ry
6. write in ROB, InstrQueue,RAT
	- if Sd, modify the counter in the ROB
		- the update() in ROB should also be changed
#### 3. execute
1. check the dependency of all entries
2. compute the offset
3. if Sd, prepare to commit
4. if Ld, prepare to memory
#### 4. memory
1. Only Ld need to go to memory
2. seach in the queue, if exist, take 1 cycle
3. if not exist, take n cycle
#### 5.writeback
1. now the cdb need to arbiter twice
	(in wb(): for i in 4, if i=0~2, go to ALU first, if i=3, go to instrQueuefirst)

#### 6.commit
1. Ld will be commited as usual
2. Sd will take more cycle to commit
	1. only in the final cycle of Sd we write in to memory
	2. Sd won't affect the RAT and ARF
## 2. memqueue implementation
#### 1. attributes
```
overall attrs
configs: latency...
Num_exec: #of enrties in the exec stage
Num_mem: #of enrties in the mem stage
entries:
|-----basic attrs------|--------------------RS-------------------|----Exec----|---------Mem-----------|----------------help---------------------|
	|type(Ld/Sd)|value|addr|tag1|tag2|value1|value2|issue counter|Exec counter|Mem counter|Mem latency|status(issue,exec,mem,wb,commit)|occupied|
```
#### 2.methods
```python
"""issue"""
def check_empty_entry()
	'''occupied == False'''
def get_empty_emtry()
def issue_load()
	'''Ld: value1: reg, value2: offset'''
	'''Sd: value1: reg, value2: offset, value: reg'''
	'''status == issue'''
	'''instr.issue = cycle'''
	'''occupied = True'''
"""exec"""
def check_empty_pu()
	'''if current Num_exec<config.max exec'''
def check_exec_ready_entry()
def get_exec_ready_entry()
def exec_load()
	'''addr = value1 + value2'''
	'''status = exec'''
def exec_run()
	'''for all entries(usually 1) in the exec stage, exec counter++'''
"""Mem"""
def check_empty_memu()
def check_mem_ready_entry()
	'''type==Ld && addr!=None && exec counter> exec latency && status == issue && occupied == true'''
def get_mem_ready_entry()
def mem_load()
	'''looking for the same addr in the entries, if find mem latency =1, else latency = n'''
	'''self.status = mem'''
def mem_run()
"""write back"""
def check_wb_ready_entry
def get_wb_ready_entry
def wb(tag, value)
def wb_load()
	'''change status, add a timestamp on instr'''
"""commit"""
def commit()
```