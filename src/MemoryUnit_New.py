"""
Memory Unit

attributes
 -


methods
 - 
"""

from Instruction import Instruction
import logging

class Mem_entry:
    
    def __init__(self):
        #Basic
        self.Type = None
        self.addr = None                    # offset + tag_value  (operand 2)
        self.instr = None  
        #For RS
        self.target = None                #(operand 1) 
        self.offset:int = None              #must be a int
        self.operand2 = None                #(operand 2)
        self.tag_operand1 = None            #tag for operand 1
        self.value_operand1 = None          #value for operand 2
        self.tag_operand2 = None            #tag for operand 2
        self.value_operand2 = None          #value foroperand 2
        self.ready_for_exec = False         #when True, represent this entry can enter exec stage

        #For Exec
        self.exec_counter = None     #only this two flag is True, can go to Mem stage OR Commit stage*****2

        #For Mem
        self.current_mem_cycle = 0                 # +1 in update function
        self.total_mem_cycle = 5                  #forwading is 1 cycle, going to mem is latancy_in_memory

        #For help
        self.status = None       #can be          issue   exec   mem   wb    commit
        self.occupied = False

    def __str__(self):
        str_ = ''
        str_ += str(self.Type) + '|' + '\t' +str(self.addr) + '|' + '\t' +str(self.target) + '|' + '\t' +str(self.offset) + '|' + '\t'
        
        str_ += str(self.tag_operand1) + '|' + '\t' +str(self.value_operand1) + '|' + '\t' +str(self.tag_operand2) + '|' + '\t' +str(self.value_operand2) +'|'+ '\t'
        str_ += str(self.exec_counter) +'/1'+'|'+ '\t\t' +str(self.ready_for_exec) + '|'+ '\t\t' +str(self.status) + '|' + '\t'
        str_ += str(self.current_mem_cycle) + '/'+ str(self.total_mem_cycle)
        return str_

    def clean(self):
        self.__init__()

class MemoryUnit:
    def __init__(self,number_RS:int,latancy_in_memory:int,Mem_data:dict) -> None:
        self.number_RS = number_RS
        self.exec_latency = 1
        self.latency_in_memory = latancy_in_memory
        self.latency_forwarding = 1
        self.Mem_data = Mem_data

        self.adder_occupy = False
        self.mem_occupy = False


        self.entry_list = []
        self.head = 0
       
        for i in range(self.number_RS):
            self.entry_list.append(Mem_entry())

    def __str__(self):

        str_ = ''
        str_ += "-----"+"Memory Unit"+"-----\n"
        str_ += 'type\t' + 'addr\t'+'target\t'+ 'offset\t'+'oprd1\t' + 'value1\t'+ 'oprd2\t'+'value2\t'+ 'exec_counter\t'+'ready_for_exec\t'+' Status\t' +' memCounter' +'\n'
        for i in range(self.number_RS):
            str_ +=str(self.entry_list[i].__str__()) 
            if self.head == i: str_ += "\t<--head"
            str_ +="\n"

        return str_

    def increase_ptr(self,ptr):
        ptr += 1
        if ptr >= self.number_RS:
            ptr = 0
        return ptr
    
#### For issue:
    def check_empty_entry(self):
        if self.entry_list[self.head].occupied == True:
            return False
        return True
    
    def get_empty_entry(self):
        return self.head
    
    def issue_load(self,instr:Instruction,idx:int,type_,target,offset,tag_operand2,value_operand2,tag_operand1,value_operand1):
        self.entry_list[idx].occupied = True
        self.entry_list[idx].Type = type_  ##Ld OR Sd
        self.entry_list[idx].status = 'issue'
        self.entry_list[idx].instr = instr
       
        self.entry_list[idx].Type = type_
        self.entry_list[idx].target = target
        self.entry_list[idx].offset = offset
        self.entry_list[idx].tag_operand1 = tag_operand1
        self.entry_list[idx].value_operand1 = value_operand1
        self.entry_list[idx].tag_operand2 = tag_operand2
        self.entry_list[idx].value_operand2 = value_operand2
        logging.info('In the memort_load, RS idx = {}, load detail are operand1=({})//operand2=({})//operand3=()'.format(idx,target,offset,))
        self.head = self.increase_ptr(self.head)    

#### For exce:
    def check_empty_FU(self):
        if self.adder_occupy == True:
            return False
        return True
    
    def check_issue_ready(self,idx):#Ld, addr dependency solved; Sd: addr and value dependency solved
        entry:Mem_entry = self.entry_list[idx]
        if entry.Type == "Ld":
            if(entry.value_operand2 !=None) and (entry.tag_operand2 == None) and (entry.ready_for_exec) and (entry.status == "issue"):
                return True
            else: 
                return False
        else:#for Sd
            if(entry.value_operand2 !=None) and (entry.tag_operand2 ==None) and (entry.value_operand1 !=None) and (entry.tag_operand1 ==None) and (entry.ready_for_exec) and (entry.status == "issue"):
                return True
            else: 
                return False
    
    def get_issue_ready_entry(self):
        for i in range(self.number_RS):
            if self.check_issue_ready(i):
                return i
        return None

    def exec_load(self,idx):
        self.entry_list[idx].status = 'exec'
        self.entry_list[idx].exec_counter = -1
        self.adder_occupy = True
        self.entry_list[idx].addr = self.entry_list[idx].value_operand2 + int(self.entry_list[idx].offset)

    def exec_run(self):
        for i in range(self.number_RS):
            if self.entry_list[i].status == 'exec':
                self.entry_list[i].exec_counter += 1


    def check_exec_ready_entry(self,idx):
        if self.entry_list[idx].exec_counter >= self.exec_latency and self.entry_list[idx].status == 'exec':
            return True
        return False


#### For Memory stage:
    def check_empty_memu(self):
        if self.mem_occupy == False:
            return True
        else:
            return False
    
    def get_mem_prepared_entry(self):
        idx = None# if we can't find, return none
        # base = self.head
        for i in range(self.number_RS):
            entry:Mem_entry = self.entry_list[i]
            if entry.occupied:#first check occupied
                if entry.Type == "Ld" and entry.status == "exec":#then check kind and status
                    if self.check_exec_ready_entry(i):#the Ld should also be ready
                        idx = i

                        return idx
        if idx == None:#if we can't find such an entry
            return None #no need for check the addr dependencies
        
    def mem_load(self,idx):
        '''switch the entry idx into the mem stage'''
        #change current stage
        self.entry_list[idx].status = "mem"
        self.adder_occupy = False
        self.mem_occupy = True

        self.entry_list[idx].current_mem_cycle = -1

        self.entry_list[idx].value_operand1 =self.Mem_data[int(self.entry_list[idx].addr)]

    def mem_run(self):
        for i in range(self.number_RS):
            if self.entry_list[i].status == "mem":
                self.entry_list[i].current_mem_cycle += 1

#### For writeback:

    def get_wb_prepared_entry(self):
        ''' a entry is able to write back is
        # 1. LD
        # 2. in mem
        # 3. counter satisfied'''
        idx = None
        for i in range(self.number_RS):
            entry:Mem_entry = self.entry_list[i]
            if entry.Type == "Ld" and entry.status =="mem":
                if entry.current_mem_cycle >= entry.total_mem_cycle:
                    idx = i
                    return idx
        return None

    def write_back_offload(self,idx):
        '''if we decide to offload this entry, we need
            1. keep target and value
            2. clean this entry'''
        self.entry_list[idx].status = "wb"
        target = self.entry_list[idx].target
        value = self.entry_list[idx].value_operand1
        instr = self.entry_list[idx].instr
        type_ = self.entry_list[idx].Type
        
        self.entry_list[idx].clean()
        self.mem_occupy = False

        return {"type":type_,"target":target,"target_value":value,"instr":instr}

    def write_back(self, target, value):
        for i in range(self.number_RS):
            
            entry:Mem_entry = self.entry_list[i]
            if entry.occupied:
                if entry.tag_operand2 == target:
                    entry.tag_operand2 =None
                    entry.value_operand2 = value
                if entry.tag_operand1 == target:
                    entry.tag_operand1 =None
                    entry.value_operand1 = value

#### For Commit stage:
    def check_commit_prepared_entry(self,idx):
        entry:Mem_entry = self.entry_list[idx]
        if entry.Type != "Sd":
            return False#Ld shouldn't use this
        if entry.status == "exec":
            if self.check_exec_ready_entry(idx):
                return True
        return False

    def sign_commit_entry(self,idx):#move entry outside the exec, but do not clean the entry
        self.entry_list[idx].status = "commit"
        self.adder_occupy = False
        # return the instr
        return [self.entry_list[idx].instr, self.entry_list[idx].target]

    def commit_offload(self,idx):#write the entry into memory, clean the entry
        # write current value back to the given addr
        addr = int(self.entry_list[idx].addr)
        value = float(self.entry_list[idx].value_operand1)
        self.Mem_data[addr] = value
        logging.info("memoryUnit.commit_offload():write {} to addr {}".format(value,addr))
        #clean the entry
        self.entry_list[idx].clean()




    def update(self):
        for i in range (self.number_RS):
            entry:Mem_entry = self.entry_list[i]
            if entry.status == 'issue':
                if entry.tag_operand2 == None and entry.value_operand2 != None:
                    entry.ready_for_exec = True
            elif entry.status == 'exec':
                pass
            elif entry.status == 'mem':
                pass
            elif entry.status == 'wb':
                pass
            elif entry.status == 'commit':
                pass
                

########################################################################################################################################################
    


    

    

        



        


        
        




