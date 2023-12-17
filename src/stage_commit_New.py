"""
Commit Stage


Components
"""

from Instruction import *
from ReorderBuffer import *
from RegisterAliasTable import *
from ArchitecturalRegisterFile import *
from InstructionQueue import *
from ReservationStations import *
from ProcessingUnits import *
from InstructionMemory import *
from output import OutputHandler
import logging
from BranchUnit import BranchUnit
from MemoryUnit_New import MemoryUnit



def Commit(reorderBuffer:ReorderBuffer,registerAliasTable:RegisterAliasTable,
           architecturalRegisterFile:ArchitecturalRegisterFile, outputHandler:OutputHandler,branchUnit:BranchUnit,memoryUnit:MemoryUnit,cycle:int):
    #memory
    #check all entries
    #when a ready entry will be signed as ready for commit
    for idx in range(memoryUnit.number_RS):
        if memoryUnit.check_commit_prepared_entry(idx):#its ready to commit
            #memu side:
            [instr,tag] = memoryUnit.sign_commit_entry(idx)
            #rob side
            reorderBuffer.Key_Value[tag][1] = idx #will be use in mem commit
            reorderBuffer.Key_Value[tag][2] = True
            reorderBuffer.Key_Value[tag][3] = instr

    #Branch Prediction
    #new checking: we shouldn't begin commit when the system is still in branch prediction
    if (branchUnit.in_prediction):
        logging.info("cycle{}-Commit: Commit blocked since system is in branch prediction".format(cycle))
        return
    if (not reorderBuffer.check_ready()):
        logging.info("cycle{}-Commit: no ready entry in ROB".format(cycle))
        return
       
    #pop out the instr from ROB
    instr, value = reorderBuffer.commit()
    instr:Instruction
    instr.commit = cycle

    #Change values
    #here for the Sd, Bne and Beq, we don't need to do anything with RAT and ARF
    if (not "Bne" in instr.type) and (not "Beq" in instr.type) and (not "Sd" in instr.type):
        registerAliasTable.commit(instr.operand1, value, instr)
        architecturalRegisterFile.commit(instr.operand1, value)

    #memory
    #additional things should be done for memory operations
    if "Sd" in instr.type:  
        idx = value                     #strange but right.......
        memoryUnit.commit_offload(idx)
    
    #output management
    outputHandler.get_instr(instr)
    outputHandler.get_ARF(architecturalRegisterFile)
    


    