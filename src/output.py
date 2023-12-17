"""
Output Stage
class: output andler
- help functions for converting the data to align the output format
- keep commited instrs for their history

"""
import logging
from Instruction import Instruction
from ArchitecturalRegisterFile import ArchitecturalRegisterFile
class OutputHandler:
    def __init__(self,config:dict) -> None:
        self.instrs = []
        self.ARF = 0
        self.configs = config 
        """ {
        "Add":1,"Addi":1,"Sub":1,"NOP":1,"Add.d":4,"Sub.d":4,"Mult.d":15,"memExecLatency":1,"memMemLatency":4
        }"""
        
    def get_instr(self,instr:Instruction):
        '''add a (committed) instr to the list'''
        # #check the format
        # for cycle in [instr.issue,instr.execute,instr.writeback,instr.commit]:
        #     if cycle == None:
        #         logging.info("OutputHandler.get_instr(): getting invalid instr:({})".format(instr.__str__()))
        
        #switch
        # if instr.type in ['Add','Addi','Sub','Add.d','Sub.d','Mult.d','NOP']:
        #     instr.execute = '{}-{}'.format(instr.execute,instr.execute + self.configs[instr.type] -1)
        #     instr.memory = 'X-X'
        #     instr.commit = '{}-{}'.format(instr.commit,instr.commit)
        # # if instr.type in ['Ld','Sd']:
        #     xxxxxx


        self.instrs.append(instr)

    def get_ARF(self, ARF:ArchitecturalRegisterFile):
        
        self.ARF = ARF

    # def get_Memory(self, Memory:ArchitecturalRegisterFile):
        
    #     self.Memory = Memory
    def __str__(self) -> str:
        str_ =""
        str_ += "-----OutputHandler-----\n"
        str_ += "Instr\t\t\t\tIS\tEX\tMEM\tWB\tCOM" + "\n"
        for instr in self.instrs:
            str_ += instr.__str__() +"\n"
            
        
        
        str_ += "\n" + "-----ARF Data-----" + "\n"
        if self.ARF != 0:
            for i in self.ARF.Key_Value:
                if ("R" in i) and (isinstance(self.ARF.Key_Value[i],float)):
                    self.ARF.Key_Value[i] = int(self.ARF.Key_Value[i])
                
                str_ += i + " = " + str(self.ARF.Key_Value[i]) + "\n"
        str_ += "\n" + "-----Memory Data-----" + "\n"

        return str_
        
class OutputHandler_fetch:
    def __init__(self,config:dict) -> None:
        self.instrs = []
        self.ARF = 0
        self.configs = config 
        """ {
        "Add":1,"Addi":1,"Sub":1,"NOP":1,"Add.d":4,"Sub.d":4,"Mult.d":15,"memExecLatency":1,"memMemLatency":4
        }"""
        
    def get_instr(self,instr:Instruction):
        '''add a (committed) instr to the list'''
        #check the format
        for cycle in [instr.issue,instr.execute,instr.writeback,instr.commit]:
            if cycle == None:
                logging.info("OutputHandler.get_instr(): getting invalid instr:({})".format(instr.__str__()))
        
        #switch
        # if instr.type in ['Add','Addi','Sub','Add.d','Sub.d','Mult.d','NOP']:
        #     instr.execute = '{}-{}'.format(instr.execute,instr.execute + self.configs[instr.type] -1)
        #     instr.memory = 'X-X'
        #     instr.commit = '{}-{}'.format(instr.commit,instr.commit)
        # # if instr.type in ['Ld','Sd']:
        #     xxxxxx


        self.instrs.append(instr)



    # def get_Memory(self, Memory:ArchitecturalRegisterFile):
        
    #     self.Memory = Memory
    def __str__(self) -> str:
        str_ =""
        str_ += "-----OutputHandler_fetch-----\n"
        str_ += "Instr\t\t\t\tIS\tEX\tMEM\tWB\tCOM" + "\n"
        for instr in self.instrs:
            str_ += instr.__str__() +"\n"
            
    

        return str_
        



    
    


    