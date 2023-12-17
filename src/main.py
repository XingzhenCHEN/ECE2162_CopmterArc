"""
imports
"""
import logging
import copy
import os
# logging.basicConfig(level="INFO")
# components
from Instruction import Instruction
from InstructionMemory import InstructionMemory
from InstructionQueue import InstructionQueue
from ReorderBuffer import ReorderBuffer
from RegisterAliasTable import RegisterAliasTable
from ArchitecturalRegisterFile import ArchitecturalRegisterFile
from ReservationStations import ReservationStations
from ProcessingUnits import ProcessingUnits, PU_config

#branch prediction
from BranchUnit import BranchUnit
from MemoryUnit_New import MemoryUnit
#TODO: add memory and branch units

# stages
from stage_init import Config
from stage_fetch import Fetch
from stage_issue_New import Issue
from stage_execute_New import Execute
from stage_memory_New import Memory_stage
from stage_writeback_New import WriteBack
from stage_commit_New import Commit
from stage_update_New import Update
from output import OutputHandler
from output import OutputHandler_fetch
"""
Initialization
"""
###
# get the configs
init_config = Config()
init_config.parse(os.path.realpath("inputs")+"\\TestCase1.txt")
init_config.numFReg = 32
init_config.numRReg = 32
print(init_config.__str__())
#TODO: add code for parsing outside configs
###
# instantiate the components
instructionMemory = InstructionMemory()
instructionQueue = InstructionQueue(init_config.getInstrQueueConfig()["size"])
reorderBuffer = ReorderBuffer(init_config.getROBConfig()["size"])
registerAliasTable = RegisterAliasTable(init_config.getRATConfig()["size1"],init_config.getRATConfig()["size2"])
architecturalRegisterFile = ArchitecturalRegisterFile(init_config.getARFConfig()["size1"],init_config.getARFConfig()["size2"])
reservationStations = ReservationStations(init_config.getRSConfig())
processingUnits = ProcessingUnits(init_config.getPUConfig())
outputHandler = OutputHandler(init_config.getOutputConfig())
outputHandler.get_ARF(architecturalRegisterFile)
outputHandler_fetch = OutputHandler_fetch(init_config.getOutputConfig())
#branch
branchUnit = BranchUnit()
memoryUnit = MemoryUnit(100,5,init_config.dataMemInfo)

###
# load Instrs
for instr in init_config.instrMemInfo:
    instructionMemory.push(instr)
# load Regs
reg_names = []
reg_values = []
for reg_name in init_config.regInfo:
    reg_names.append(reg_name)
    reg_values.append(init_config.regInfo[reg_name])
architecturalRegisterFile.push(reg_names,reg_values)
#TODO: load data
# print(instructionMemory)
# print(instructionQueue)
# print(reorderBuffer)
# print(registerAliasTable)
# print(architecturalRegisterFile)
# print(reservationStations)
# print(processingUnits)
###
# run

cycle = 0
while cycle<90:
    print("#####---cycle:{}---##################################".format(cycle))
    print("Fetching...")
    Fetch(instructionMemory,instructionQueue,branchUnit,outputHandler_fetch,cycle)
    print("Issuing")
    Issue(instructionQueue,reorderBuffer,registerAliasTable,architecturalRegisterFile,reservationStations,outputHandler,branchUnit,memoryUnit,cycle)
    ###branch prediction
    ###Snapshot here
    if(branchUnit.snapshot_signal):
        logging.info("cycle{}-main(): branch prediction begins, taking snapshot".format(cycle))
        #snapshot components:instructionQueue,reorderBuffer,registerAliasTable,architecturalRegisterFile,reservationStations,processingUnits
        branchUnit.snapshots["instructionQueue"] = InstructionQueue(init_config.getInstrQueueConfig()["size"])# if a mis prediction happens, the new instr queue will be empty since all instrs fetched later will be wrong
        branchUnit.snapshots["reorderBuffer"] = copy.deepcopy(reorderBuffer)
        branchUnit.snapshots["registerAliasTable"] = copy.deepcopy(registerAliasTable)
        branchUnit.snapshots["architecturalRegisterFile"] = copy.deepcopy(architecturalRegisterFile)
        branchUnit.snapshots["reservationStations"] = copy.deepcopy(reservationStations)
        branchUnit.snapshots["processingUnits"] = copy.deepcopy(processingUnits)
        branchUnit.snapshots["memoryUnit"] = copy.deepcopy(memoryUnit)
        branchUnit.snapshot_signal = False     
    print("Executing")
    Execute(reservationStations,processingUnits,branchUnit,memoryUnit,cycle)
    if(branchUnit.roll_back_signal):
        logging.warning("cycle{}-main(): beginning roll back execution".format(cycle))
        #reloading all components
        instructionQueue = branchUnit.snapshots["instructionQueue"]# in backward we don't need deepcopy
        reorderBuffer = branchUnit.snapshots["reorderBuffer"]
        registerAliasTable = branchUnit.snapshots["registerAliasTable"]
        architecturalRegisterFile = branchUnit.snapshots["architecturalRegisterFile"]
        reservationStations = branchUnit.snapshots["reservationStations"]
        processingUnits = branchUnit.snapshots["processingUnits"]
        memoryUnit = branchUnit.snapshots["memoryUnit"]
        #reset branchunit
        branchUnit.roll_back_signal = False
        # branchUnit.strategy = not branchUnit.strategy#change to correct strategy
        branchUnit.addr_branch = branchUnit.addr_branch_real
        if branchUnit.strategy:
            instructionQueue.pc = int(branchUnit.addr_branch_real)
            # print(branchUnit.addr_branch_real)
        else:
            instructionQueue.pc = int(branchUnit.addr_nbranch)
        logging.warning("cycle{}-main():rolling-back complete, pc changed to:{}, finishing the remain cycle of snapshot".format(cycle,instructionQueue.pc))
        cycle += 1
        print("#####---cycle:{}---##################################".format(cycle))
        print("Executing")
        Execute(reservationStations,processingUnits,branchUnit,memoryUnit,cycle)
    print("Memory")
    Memory_stage(memoryUnit,cycle)
    print("Writing back")
    WriteBack(processingUnits,reservationStations,reorderBuffer,memoryUnit,cycle)
    print("Comitting")
    Commit(reorderBuffer,registerAliasTable,architecturalRegisterFile,outputHandler,branchUnit,memoryUnit,cycle)
    print("updating")
    Update(instructionQueue,reservationStations,reorderBuffer,memoryUnit)
    cycle += 1


# print(instructionQueue)
# print(reorderBuffer)
# print(registerAliasTable)
# print(architecturalRegisterFile)
# print(reservationStations)
# print(processingUnits)
# print(memoryUnit)
# print(memoryUnit.Mem_data)
print(outputHandler)

str_ = ''
for i in memoryUnit.Mem_data:
    str_ += "Mem[{}]= {} | ".format(i,memoryUnit.Mem_data[i]) 
str_ += '\n'
print(str_)
print(outputHandler_fetch)
print(branchUnit)

    