"""
stage writeback:
1. check
2. get a instr from the PUs
3. write the instr back to RS, ROB (no need to write to RAT)

TODO: add more instrs of memory
"""
import logging
from ProcessingUnits import ProcessingUnits, PU_config
from ReservationStations import ReservationStations
from ReorderBuffer import ReorderBuffer
from MemoryUnit_New import MemoryUnit


def WriteBack(processingUnits:ProcessingUnits, 
              reservationStations:ReservationStations,
              reorderBuffer:ReorderBuffer,memoryUnit:MemoryUnit,cycle:int):
    
    #here we always wb Ld instrs first since they're too slow
    idx = memoryUnit.get_wb_prepared_entry()
    print("in writeback, the idx is",idx)
    if idx != None: #we have something to wb
        wb_info = memoryUnit.write_back_offload(idx)
        assert isinstance(wb_info, dict), logging.error("cycle{}: in writeBack(): invalid return value from pu.offload(), need dict, found{}"
                                                        .format(cycle, type(wb_info)))
        #modify the cycle of wb
        wb_info["instr"].writeback = cycle
        #2.1. write back to RS
        reservationStations.write_back(tag = wb_info["target"],value = wb_info["target_value"])
        #2.2 write back to ROB
        reorderBuffer.writeback(instr = wb_info["instr"],rob_name = wb_info["target"],value = wb_info["target_value"])
        #2.3 write back to memu
        memoryUnit.write_back(target = wb_info["target"],value = wb_info["target_value"])
        return


    #1. check availability
    cid, idx = processingUnits.check_ready_entry()
    logging.info("WriteBack:get({},{})".format(cid,idx))
    if cid != None:
        #if there is something to writeback
        wb_info = processingUnits.offload(cid,idx,cycle)#wb_info {"type","target","target_value","instr"}
        assert isinstance(wb_info, dict), logging.error("cycle{}: in writeBack(): invalid return value from pu.offload(), need dict, found{}"
                                                        .format(cycle, type(wb_info)))
        for attr in ["type","target","target_value","instr"]:
            assert attr in wb_info, logging.error("cycle{}: in writeBack(): invalid return value from pu.offload(): missing {}"
                                                  .format(cycle,attr))
        #2.1. write back to RS
        reservationStations.write_back(tag=wb_info["target"],value=wb_info["target_value"])
        #2.2 write back to ROB
        reorderBuffer.writeback(instr=wb_info["instr"],rob_name=wb_info["target"],value=wb_info["target_value"])
        #2.3 write back to memu
        memoryUnit.write_back(target=wb_info["target"],value=wb_info["target_value"])

