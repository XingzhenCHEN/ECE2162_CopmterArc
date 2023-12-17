"""
execute stage

components:
Reservation stations, Processing Units

tasks:
 - for each cluster of reservation station, check availablity and send to PUs
 - PUs will execute then
"""
from ReservationStations import ReservationStations
from ProcessingUnits import ProcessingUnits,PU_config
from Instruction import Instruction
from BranchUnit import BranchUnit
from MemoryUnit_New import MemoryUnit
import logging

def Execute(reservationStations:ReservationStations, processingUnits:ProcessingUnits,branchUnit:BranchUnit,memoryUnit:MemoryUnit,cycle):
    
    # STEP1: push from RS to PU
    # here we rule that the corresponding RS_cluster and PU_cluster have the same name, i.e., cid
    for cid in reservationStations.RS_clusters:# for each cluster
        idx_out = reservationStations.check_ready_entry(cid)
        if idx_out == -1:
            continue
        idx_in = processingUnits.check_empty_entry(cid)
        if idx_in == -1:
            continue
        # get RS's output
        output_info = reservationStations.offload(cid,idx_out,cycle)
        logging.info("cycle{}:push{} from RS({},{})to PU({},{})".format(cycle,output_info,cid,idx_out,cid,idx_in))
        processingUnits.load(cid, idx_in,output_info)
    
    ##Branch prediction
    ##here we check all the PUs inside the adder, to find out if a branch prediction is matureS
    for PU in processingUnits.PU_clusters["Integer adder"].PUs:
        #find the branch instr
        if(not PU.check_occupied()):#if the PU is empty, the we do nothing
            continue
        if(not "Bne" in PU.type) and (not "Beq" in PU.type):
            continue
        if PU.exec_counter + 1 >= PU.config.get_latency(PU.type):# this PU with branch instr will be ready after this cycle's exec
            logging.warning("cycle{}-execute(): branch detected, begin to branch speculation".format(cycle))
            is_misprediction = branchUnit.check_misprediction(PU.target_value)
            logging.warning("target value:{}".format(PU.target_value))
            logging.warning("cycle{}-execute(): misprediction is {}: PU:{}, strategy:{}".format(cycle,is_misprediction,PU.__str__(),branchUnit.strategy))
            #update the predictor
            branchUnit.predictor.update_status(PU.instr,PU.target_value)
            # print(branchUnit)
            #update the target
            if PU.target_value == True:
                    logging.warning("updating target value")
                    branchUnit.predictor.update_target(PU.instr,int(branchUnit.addr_branch_real))

            if(not is_misprediction):#all is good, just clean the whole entry
                branchUnit.clean()
            else:#prepare to do the rollback
                branchUnit.roll_back_signal = True
                branchUnit.strategy = PU.target_value
                #after roll_back, next time we meet the instr, we shouldn't do prediction
            
    processingUnits.execute()

    if memoryUnit.check_empty_FU():
        
        idx = memoryUnit.get_issue_ready_entry()
        if idx == None:
            pass
        else:
            print('get into exec_load for idx:{}'.format(idx))
            memoryUnit.exec_load(idx)
            logging.info('cycle{}-execute():idx{}: load branch instr '.format(cycle,idx))
            #update the instr
            memoryUnit.entry_list[idx].instr.execute = cycle
    memoryUnit.exec_run()
    # if the exec is complete, we should empty the room
    


        

if __name__ == '__main__':
    #test codes
    #init: 
    #1. init RS
    logging.basicConfig(level="INFO")
    config1 = {"name":"Int","instr_list":["ADDI","SUBI"],"size":3}
    config2 = {"name":"Double","instr_list":["ADDD","SUBD"],"size":3}
    rs = ReservationStations([config1,config2])

    config = PU_config()
    I_con = {"name":"Int", "instr_list":["ADDI","SUBI"],"size":2,"buffer_size":1,"config":config}
    F_con = {"name":"Double", "instr_list":["ADDD","SUBD"],"size":2,"buffer_size":1,"config":config}# need to keep the same name and instr_list
    pus = ProcessingUnits([I_con,F_con])

    for cycle in range(35):
        print("##########cycle:{}##########".format(cycle))
        print("sim issue stage")
        # try to load to rs(issue)
        type_ = ""
        if(cycle%2 == 0):
            type_ = "ADDI"
        else:
            type_ = "ADDD"
        cid = rs.check_instr_name(type_)
        idx = rs.check_empty_entry(cid)
        if idx != -1:
            rs.load(cid,idx,Instruction(type_,"R{}".format(cycle+1),cycle,cycle+1),"ROB{}".format(cycle),cycle,cycle+1)
            print("load instr {} at ({},{})".format(Instruction(type_,"R{}".format(cycle+1),cycle,cycle+1).__str__(),cid,idx))
        
        # try to execute
        print("exec stage")
        Execute(rs,pus,cycle)

        #try to output(writeback)
        print("sim writeback stage")
        if cycle>30:
            cid, idx = pus.check_ready_entry()
            if cid != None:
                info = pus.offload(cid,idx,cycle)
                print("offload info{} at ({},{})".format(info,cid,idx))
                print("instr info:",info["instr"].__str__())

        print("sim update stage")
        rs.update()
        print(rs)
        print(pus)

