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
    instance_count = 0

    def __init__(self) -> None:
        #Basic
        self.Type = None
        self.addr = None   # offset + tag_value  (operand 2)
        self.instr = None
        #For RS
        self.target = None   #(operand 1) 
        self.offset = None         # must be a int
        self.tag1 = None            
        self.value1 = None
        self.tag0 = None
        self.value0 = None
        self.ready_for_exec = False

        #For Exec
        self.exec_counter = None              #only this two flag is True, can go to Mem stage OR Commit stage*****2

        #For Mem
        self.mem_counter = 0                 # +1 in update function
        self.need_cycle = 0                  #forwading is 1 cycle, going to mem is latancy_in_memory

        #For help
        # self.No = None        #For checking forwarding
        self.Status = None       #can be          issue   exec   mem   wb    commit
        self.occupied = False

    def __str__(self):
        str_ = ''
        str_ += str(self.Type) + '|' + '\t' +str(self.addr) + '|' + '\t' +str(self.target) + '|' + '\t' +str(self.offset) + '|' + '\t'
        
        str_ += str(self.tag1) + '|' + '\t' +str(self.value1) + '|' + '\t' +str(self.tag0) + '|' + '\t' +str(self.value0) +'|'+ '\t'
        str_ += str(self.exec_counter) +'/1'+'|'+ '\t\t' +str(self.ready_for_exec) + '|'+ '\t\t' +str(self.Status) + '|' + '\t'
        str_ += str(self.mem_counter) + '/'+ str(self.need_cycle)
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

        self.adder_maxnum = 1
        self.adder_nownum = 0
        self.mem_maxnum = 1
        self.mem_nownum = 0

        self.entry_list = []
        self.head = 0
        
        
        
        for i in range(self.number_RS):
            self.entry_list.append(Mem_entry())

    def __str__(self):

        str_ = ''
        str_ += "-----"+"Memory Unit"+"-----\n"
        str_ += 'type\t' + 'addr\t'+'target\t'+ 'offset\t'+'tag1\t' + 'value1\t'+ 'tag0\t'+'value0\t'+ 'exec_finish\t'+'ready_for_exec\t'+' Status\t' +' memCounter' +'\n'
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

    def check_empty_entry(self):
        if self.entry_list[self.head].occupied == True:
            return False
        return True
    
    def get_empty_entry(self):
        return self.head

    def issue_load(self,instr:Instruction,idx:int,type_,target,offset,tag1,value1,tag0,value0):
        self.entry_list[idx].occupied = True
        self.entry_list[idx].Type = type_  ##Ld OR Sd
        self.entry_list[idx].Status = 'issue'
        self.entry_list[idx].instr = instr
       
        self.entry_list[idx].Type = type_
        self.entry_list[idx].target = target
        self.entry_list[idx].offset = offset
        self.entry_list[idx].tag1 = tag1
        self.entry_list[idx].value1 = value1
        self.entry_list[idx].tag0 = tag0
        self.entry_list[idx].value0 = value0
        logging.info('In the memort_load, RS idx = {}, load detail are operand1=({})//operand2=({})//operand3=()'.format(idx,target,offset))
        self.head = self.increase_ptr(self.head)

    def check_empty_FU(self):
        if self.adder_nownum < self.adder_maxnum:
            return True
        return True
    
    def update(self):
        for i in range(self.number_RS):
            if self.entry_list[i].Status == 'issue':
                if (self.entry_list[i].tag1 == None) and (self.entry_list[i].value1 != None) and (self.entry_list[i].Status == 'issue'):
                    self.entry_list[i].ready_for_exec = True
                    
    def check_issue_ready(self,idx):#Ld, addr dependency solved; Sd: addr and value dependency solved
        entry:Mem_entry = self.entry_list[idx]
        if entry.Type == "Ld":
            if(entry.value1 !=None) and (entry.tag1 ==None) and (entry.ready_for_exec) and (entry.Status == "issue"):
                return True
            else: return False
        else:#for Sd
            if(entry.value1 !=None) and (entry.tag1 ==None) and (entry.value0 !=None) and (entry.tag0 ==None) and (entry.ready_for_exec) and (entry.Status == "issue"):
                return True
            else: return False
    
    def get_issue_ready_entry(self):
        for i in range(self.number_RS):
            if self.check_issue_ready(i):
                return i
        return None
 
    def exec_load(self,idx):
        self.entry_list[idx].Status = 'exec'
        self.entry_list[idx].exec_counter = -1
        self.adder_nownum += 1
        self.entry_list[idx].addr = self.entry_list[idx].value1 + int(self.entry_list[idx].offset)
        
    def exec_run(self):
        for i in range(self.number_RS):
            if self.entry_list[i].Status == 'exec':
                self.entry_list[i].exec_counter += 1

    def check_exec_ready_entry(self,idx):
        if self.entry_list[idx].exec_counter >= self.exec_latency and self.entry_list[idx].Status == 'exec':
            return True
        return False
    
    def check_empty_memu(self):
        # return self.mem_nownum < self.mem_maxnum
        return True

    def check_mem_prepared_entry(self):
        #several rules apply when trying to find an entry in the memory stage
        # 1. a load entry
        # 2. all the st entry before this load entry is computed(exec_ready, )
        idx = None# if we can't find, return none
        base = self.head
        for i in range(self.number_RS):
            ptr = (base + i)%self.number_RS#search from the very old to very new
            entry:Mem_entry = self.entry_list[ptr]
            if entry.occupied:#first check occupied
                if entry.Type == "Ld" and entry.Status == "exec":#then check kind and status
                    if self.check_exec_ready_entry(ptr):#the Ld should also be ready
                        idx = ptr
                        self.adder_nownum -=1
        
        if idx == None:#if we can't find such an entry
            return None #no need for check the addr dependencies
        
        #search from old to new
        i = self.head
        while(i != idx):
            entry:Mem_entry = self.entry_list[i]
            if entry.occupied:#check occupied
                if entry.Type == "Sd":#we only care about Sd
                    if entry.addr == None:
                        logging.info("memoryUnit: fail in entering mem stage since addrs not resolved")
                        return None# if the addr is not computed, return None
                    elif self.entry_list[i].exec_counter < self.exec_latency:# have addr, but not finish exec
                        logging.info("memoryUnit: fail in entering mem stage since exec haven't finished")
                        return None
            i = self.increase_ptr(i) #move i to a new one
        #after check, we can return the idx
        return idx
            
    def check_forwarding(self,idx):
        '''begin from a given idx(the idx of a prepared ld instr), check if forwarding is needed'''
        addr = self.entry_list[idx].addr
        forward_value = None
        i = self.head
        while(i != idx):
            entry:Mem_entry = self.entry_list[i]
            if entry.occupied:#check occupied
                if entry.Type == "Sd":#we only care about Sd
                    if entry.addr == addr:#we find a matching entry
                        forward_value = entry.value0
                        assert forward_value != None
                        #here we don't break, to let new possible matching entries replace old ones
            i = self.increase_ptr(i) #move i to a new one
        return forward_value
    
    def mem_load(self,idx,forward_value):
        '''switch the entry idx into the mem stage'''
        #change current stage
        self.entry_list[idx].Status = "mem"
        self.adder_nownum -= 1
        self.mem_nownum += 1
        #set counters based on forward value
        self.entry_list[idx].mem_counter = -1
        if forward_value == None:#need to go to memory
            self.entry_list[idx].need_cycle = self.latency_in_memory
        else:#only need forwarding
            self.entry_list[idx].need_cycle = self.latency_forwarding
        
        #get the final result
        self.entry_list[idx].value0 = forward_value
        if self.entry_list[idx].value0 == None:
            self.entry_list[idx].value0 =self.Mem_data[int(self.entry_list[idx].addr)]

    def mem_run(self):
        for i in range(self.number_RS):
            if self.entry_list[i].Status == "mem":
                self.entry_list[i].mem_counter +=1

    def check_wb_prepared_entry(self):
        ''' a entry is able to write back is
        # 1. LD
        # 2. in mem
        # 3. counter satisfied'''
        idx =None
        for i in range(self.number_RS):
            entry:Mem_entry = self.entry_list[i]
            if entry.Type == "Ld" and entry.Status =="mem":
                if entry.mem_counter >= entry.need_cycle:
                    idx = i
                    return idx
        return idx

    def write_back_offload(self,idx):
        '''if we decide to offload this entry, we need
            1. keep target and value
            2. clean this entry'''
        target = self.entry_list[idx].target
        value = self.entry_list[idx].value0
        instr = self.entry_list[idx].instr
        type_ = self.entry_list[idx].Type
        
        self.entry_list[idx].clean()
        self.mem_nownum -= 1

        return {"type":type_,"target":target,"target_value":value,"instr":instr}
    
    def write_back(self, target, value):
        for i in range(self.number_RS):
            # if self.entry_list[i].occupied:
            #     continue
            #check tag0
            if self.entry_list[i].tag1 == target:
                self.entry_list[i].tag1 =None
                self.entry_list[i].value1 = value
            if self.entry_list[i].tag0 == target:
                self.entry_list[i].tag0 =None
                self.entry_list[i].value0 = value

    def check_commit_prepared_entry(self,idx):#check each entry separetly
        entry:Mem_entry = self.entry_list[idx]
        if entry.Type != "Sd":
            return False#Ld shouldn't use this
        if self.entry_list[idx].Status == "exec":
            if self.check_exec_ready_entry(idx):
                return True
        return False
    
    def sign_commit_entry(self,idx):#move entry outside the exec, but do not clean the entry
        self.entry_list[idx].Status = "commit"
        self.adder_nownum -= 1
        # return the instr
        return [self.entry_list[idx].instr, self.entry_list[idx].target]
    
    def commit_offload(self,idx):#write the entry into memory, clean the entry
        # write current value back to the given addr
        addr = int(self.entry_list[idx].addr)
        value = float(self.entry_list[idx].value0)
        self.Mem_data[addr] = value
        logging.info("memoryUnit.commit_offload():write {} to addr {}".format(value,addr))
        #clean the entry
        self.entry_list[idx].clean()
        



        


        
        




