"""

"""

from MemoryUnit_New import MemoryUnit
import logging
def Memory_stage(memoryUnit:MemoryUnit,cycle:int):
    #trying to move instrs from exec to mem
    if memoryUnit.check_empty_memu():#memu has empty unit
        idx = memoryUnit.get_mem_prepared_entry()
        if idx != None: #find a ready entry
            # forward_value = memoryUnit.check_forwarding(idx)      # try to do forwarding
            memoryUnit.mem_load(idx)#try to load entry
            logging.info("cycle{}:memory: idx{} begin in the memory stage".format(cycle,idx))
            #update instr info
            memoryUnit.entry_list[idx].instr.memory = cycle

    #trying to run the memory
    memoryUnit.mem_run()
    

