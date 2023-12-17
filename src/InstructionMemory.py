"""
Instruction memory
store instructions in the very begining
attributes
 - size
 - instr_length
 - instructions:{addr:instr}
 - flags:{"flag:addr"}

methods
 - push(instr)
 - fetch(addr)
 - parse()
"""
import copy
import logging
class InstructionMemory:
    def __init__(self) -> None:
        self.size = 0
        self.instr_length = 1
        self.instructions = {}
        self.flags = {}

    def __str__(self):
        str_ = ""
        str_ += "\n-----InstructionMemory-----\n"
        str_ += "addr|\tInstr\n"
        addr = 0
        while(addr < self.size):
            str_ += str(addr) + "|\t" + self.instructions[str(addr)].__str__() +"\n"
            addr += self.instr_length
        return str_

    def push(self, instr):
        "push an instr into the memory, shouldn't be used in runtime"
        addr = self.size * self.instr_length
        self.instructions[str(addr)] = instr
        self.size +=1

    def check_valid(self,addr:int):
        """check if an address is valid
        input: addr index, output:bool"""
        valid = True
        valid &= (addr%self.instr_length == 0)#check if the addr aligns the instr_length
        valid &= (addr < self.size*self.instr_length)#check if the addr is out of boundary
        return valid

    def fetch(self, addr:int):#branch prediction: add addr to instr
        """get an instr from given addr
            input: addr; output: and instruction"""
        if not (self.check_valid(addr)):
            logging.error("InstructionMemory: invalid addr")
            raise Exception("InstructionMemory: invalid addr")
        instr = copy.deepcopy(self.instructions[str(addr)])
        instr.addr = addr
        return instr
    

# if __name__ == "__main__":
#     #print("example:")
#     instrMem = InstructionMemory()
#     instrMem.push("12345")
#     instrMem.push("qwert")
#     instrMem.push("q222t")
#     instrMem.push("qw33t")
#     instrMem.push("qw444t")
#     print(instrMem.fetch(4))