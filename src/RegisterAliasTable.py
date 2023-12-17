"""
Register Alias Table

explain the relationship between a register and a ARF OR ROB


attributes
 - R_size
 - F_size
 - Key_Value  'R0' : 'ROB2' ...


methods
 - get_alias  (return ROB<num> OR ARF<num>)
 - rename
 - Clear
"""
from Instruction import *
from ReorderBuffer import *
from RegisterAliasTable import *
from ArchitecturalRegisterFile import *
from InstructionQueue import *
from ReservationStations import *
from ProcessingUnits import *
from InstructionMemory import *
import logging

class RegisterAliasTable:
    def __init__(self,size0:int,size1:int):
        self.R_size = size0
        self.F_size = size1
        self.Key_Value = {}
        for i in range(self.R_size):
            self.Key_Value['R'+str(i)] = 'R' + str(i)
        for i in range(self.F_size):
            self.Key_Value['F'+str(i)] = 'F' + str(i)


    def __str__(self):
        
        str_ = " "
        str_ += "\n-----Register Alias Table-----\n"
        for i in range(self.R_size):
            str_ += 'R' + str(i) + ' = ' + str(self.Key_Value['R'+str(i)]) + '\n'
        for i in range(self.F_size):
            str_ += 'F' + str(i) + ' = ' + str(self.Key_Value['F'+str(i)]) + '\n'
        
        return str_
    
    def get_alias(self,register_name:str):
        if register_name not in self.Key_Value:
            raise Exception("Error: The register({}) is not in RAT!".format(register_name))
        
        return self.Key_Value[register_name]
    
    def rename(self,register_name:str,change_name:str):
        if register_name not in self.Key_Value:
            raise Exception("Error: The register{} is not in RAT!".format(register_name))
        self.Key_Value[register_name] = change_name

    def commit(self,register_name:str,value:str,instr:Instruction):
        if register_name not in self.Key_Value:
            raise Exception("Error: This register is not in RAT!")
        if self.Key_Value[register_name] == instr.initial_ROB:
            self.Key_Value[register_name] = register_name
            logging.info('We can change the RAT, since the corresponding is right')
        else:
            logging.info('We can NOT change the RAT, and leave RAT')

    def Clear(self,register_name:str):
        if register_name not in self.Key_Value:
            raise Exception("Error: This register is not in RAT!")
        self.Key_Value[register_name] = register_name

if __name__ == "__main__":
    RAT = RegisterAliasTable(8,8)
    print(RAT)
    for i in range(6):
        RAT.rename("R{}".format(i),"ROB{}".format(i+2))
    print(RAT)
    
