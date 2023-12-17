"""
Reorder Buffer




attributes
 - size
 - issue_pointer
 - commit_pointer
 - num_used
 - Key_Value  'ROB<>' : 'ROB2' ...


methods
 - check_full
 - issue_push
 - get_value
 - writeback
 - check_ready
 - commit
"""

from Instruction import Instruction

class ReorderBuffer:
    def __init__(self,size:int):
        self.size = size
        self.Key_Value = {}
        self.Keys = []
        self.num_used = 0
        self.issue_pointer = 0
        self.commit_pointer = 0

        for i in range(size):
            self.Key_Value['ROB' + str(i)] = ['ROB' + str(i), None, False, 'instr',0,1]
            self.Keys.append("ROB{}".format(i))
        # 0:entry number //1:value //2:flag //3:whole instr//4:current counter//5:total latency

    def __str__(self):
        
        str_ = " "
        str_ += "\n-----Reorder Buffer-----\n"
        for i in range(self.size):
            str_ += 'ROB' + str(i) + ' => ' + str(self.Key_Value['ROB'+str(i)][0]) + ' \t| ' + str(self.Key_Value['ROB'+str(i)][1]) + ' \t| '+str(self.Key_Value['ROB'+str(i)][2]) + '   \t| ' + str(self.Key_Value['ROB'+str(i)][4]) + '/'+ str(self.Key_Value['ROB'+str(i)][5]) + '\t'
            str_ += '\t' + self.Key_Value['ROB'+str(i)][3].__str__()
            if i == self.commit_pointer:
                str_ += "<-- pointer\n"
            else:
                str_ += "\n"

        return str_
    
    def check_full(self):
        if(int(self.num_used) == int(self.size)):
            return True
        else:
            return False
        
    def issue_push(self,instr:Instruction):
        if(self.check_full()):
            raise Exception("ROB don't have enough space!")
        
        self.Key_Value['ROB' + str(self.issue_pointer)][0] = instr.operand1
        #Branch Prediction: we shouldn't give a target in ROB in branch and memory
        if("Beq" in instr.type) or ("Bne" in instr.type) or ("Sd" in instr.type):
            self.Key_Value['ROB' + str(self.issue_pointer)][0] = instr.type
        self.Key_Value['ROB' + str(self.issue_pointer)][3] = instr
        instr.initial_ROB = 'ROB' + str(self.issue_pointer)
        ROB_name = 'ROB' + str(self.issue_pointer)
        self.issue_pointer += 1
        if self.issue_pointer == self.size:
            self.issue_pointer = 0
        self.num_used += 1
        return ROB_name
    
    def get_value(self,operand):
        if operand not in self.Key_Value:
            raise Exception("Error: This operand is not in ROB!")
        return self.Key_Value[operand][1]
    
    def writeback(self,instr:Instruction,rob_name,value):
        assert rob_name in self.Key_Value, "rob_name doesn't exist"
        self.Key_Value[rob_name][1] = value
        self.Key_Value[rob_name][2] = True
        self.Key_Value[rob_name][3] = instr

    def check_ready(self):
        if self.Key_Value[self.Keys[self.commit_pointer]][2] == True and (self.Key_Value[self.Keys[self.commit_pointer]][4] >= self.Key_Value[self.Keys[self.commit_pointer]][5]):
            return True
        else:
            return False
        
    def update(self):
        for i in self.Key_Value:
            if self.Key_Value[i][2] == True:
                self.Key_Value[i][4] +=1

    def commit(self):
        '''Return a (instr, value)'''
        assert self.check_ready(), "ReorderBuffer.commit():trying to commit a unready ROB"
        instr = self.Key_Value[self.Keys[self.commit_pointer]][3]
        value = self.Key_Value[self.Keys[self.commit_pointer]][1]
        self.Key_Value[self.Keys[self.commit_pointer]][0] = self.Keys[self.commit_pointer]
        self.Key_Value[self.Keys[self.commit_pointer]][1] = None
        self.Key_Value[self.Keys[self.commit_pointer]][2] = False
        self.Key_Value[self.Keys[self.commit_pointer]][4] = 0
        self.commit_pointer += 1
        if self.commit_pointer == self.size:
            self.commit_pointer = 0
        self.num_used -= 1
        
        return (instr,value)
        
if __name__ == '__main__':
    ROB = ReorderBuffer(5)
    print(ROB)
    for cycle in range(15):
        print("##########cycle:{}##########".format(cycle))
        #simulate issue
        instr = Instruction("ADDI","R{}".format(cycle+3),"R{}".format(cycle+1),cycle+2)
        if not ROB.check_full():
            ROB.issue_push(instr)
            print("Push {} into ROB".format(instr))
        
        #simulate execute
        #simulate writeback
        if cycle >= 5 and cycle <7:
            instr = Instruction("ADDI","R100","R{}".format(cycle),cycle-3)
            ROB.writeback(instr, "ROB{}".format(cycle-5),cycle)
            print("write ROB{} with value {}".format(cycle-5,cycle))

        #simulate commot
        if cycle > 10:
            if ROB.check_ready():
                ret,val = ROB.commit()
                print("Commit {}".format(ret), " value = {}".format(val))

        print(ROB)            

