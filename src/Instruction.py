
"""
properties
	self.type #type of the instr(ADD,SUB..)
	self.operand1 #operand of this instr: number:1,2.5 ; str: 'R5', 'F3'
	self.operand2
	self.operand3 #will be the offset or pc target of Mem and Branch instrs
	self.issue #history of this instr, using cycle number 
	self.execute
	self.Memory
	self.writeBack
	self.commit
"""

class Instruction:
    def __init__(self,o_type,operand1,operand2,operand3):
	    #the init fuction
        self.type = o_type
        self.operand1 = operand1
        self.operand2 = operand2
        self.operand3 = operand3
        self.issue = None
        self.execute = None
        self.memory = None
        self.writeback = None
        self.commit = None
        self.initial_ROB = None
        self.addr = None# For branch prediction
    def __str__(self):
        # print(self.type," ",self.operand1," ",self.operand2," ",self.operand3)
        # print(      "\t",self.issue,"\t",self.execute,"\t",self.memory,"\t",self.writeback,"\t",self.commit,"\t")
        str_ = ""
        str_ += self.type + "\t"
        str_ += str(self.operand1) + "\t"
        str_ += str(self.operand2) + "\t"
        str_ += str(self.operand3) + "\t|"
        # if(self.issue != None):str_ += str(self.issue) + "\t"
        # if(self.execute != None):str_ += str(self.execute) + "\t"
        # if(self.memory != None):str_ += str(self.memory) + "\t"
        # if(self.writeback != None):str_ += str(self.writeback) + "\t"
        # if(self.commit != None):str_ += str(self.commit) 
        str_ += str(self.issue) + "\t"
        str_ += str(self.execute) + "\t"
        str_ += str(self.memory) + "\t"
        str_ += str(self.writeback) + "\t"
        str_ += str(self.commit) 
        return str_
        
        

# if __name__ == "__main__":
#     print("example instrs:")
#     instr = Instruction("ADDI", 20, 1,3)
#     print(instr)
#     instr = Instruction("LD", 'R3', "R5",20)
#     instr.issue = 1
#     instr.execute = 5
#     instr.memory = 8
#     instr.writeback = 9
#     print(instr)




