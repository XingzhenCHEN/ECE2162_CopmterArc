"""
Issue Stage


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
from BranchUnit import BranchUnit
from MemoryUnit import MemoryUnit
import logging




def Issue(instructionQueue:InstructionQueue, reorderBuffer:ReorderBuffer, registerAliasTable:RegisterAliasTable,
          architecturalRegisterFile:ArchitecturalRegisterFile, reservationStations:ReservationStations,outputHandler:OutputHandler,
          branchUnit:BranchUnit,memoryUnit:MemoryUnit,cycle:int):
    
    ## check available
    available = True
    available = available and (not instructionQueue.check_empty())
    available = available and (not reorderBuffer.check_full())
    if (not available):
        return
    
    instr:Instruction = instructionQueue.touch()

##############################################################################################################################################
###Memory
    #check instr name 
    if instr.type == 'Ld' or instr.type == 'Sd':
        if not memoryUnit.check_empty_entry():
            logging.info('Cycle {} do not have enough entry in MemoryUnit, and return'.format(cycle))
            return
        instr = instructionQueue.issue(cycle)
        idx = memoryUnit.get_empty_entry()
        logging.info("cycle{}-issue():trying to issue a memory instr({})".format(cycle,instr.__str__()))

        ##begin renaming operand 1
        
        type_ = instr.type
        [offset,reg] = instr.operand2.replace(" ", "").replace(")","").split("(")
        alias = registerAliasTable.get_alias(reg)
        if 'ROB' in alias:
            if(reorderBuffer.get_value(alias)!= None):
                value1 = reorderBuffer.get_value(alias)
                tag1 = None
            else:
                tag1 = alias
                value1 = None
        else:
            value1 = architecturalRegisterFile.get_value(alias)
            tag1 = None
        if type_ == 'Ld':
            tag0 = None
            value0 = None
        else:
            alias = registerAliasTable.get_alias(instr.operand1)
            if 'ROB' in alias:
                if(reorderBuffer.get_value(alias)!= None):
                    value0 = reorderBuffer.get_value(alias)
                    tag0 = None
                else:
                    tag0 = alias
                    value0 = None
            else:
                value0 = architecturalRegisterFile.get_value(alias)
                tag0 = None
        target = None
        if type_ == 'Ld':
            target = reorderBuffer.issue_push(instr)
            registerAliasTable.rename(instr.operand1,target)
        else:
            target = reorderBuffer.issue_push(instr)  ##target = ROB<>
        if type_ == 'Sd':#we need to change the latency of Sd units in commit
            reorderBuffer.Key_Value[target][5] = memoryUnit.latency_in_memory

        memoryUnit.issue_load(instr,idx,type_,target,offset,tag1,value1,tag0,value0)

        return

     

    c_id = reservationStations.check_instr_name(instr)
    if c_id == None :
        logging.warning('The c_id of {} is None'.format(instr))
        raise Exception

    idx = reservationStations.check_empty_entry(c_id)
    if idx == -1:
        logging.info('no enough empty entry and return in cycle{}'.format(cycle))
        return
    
    ##Finish check and begin to pop the instr
    instr = instructionQueue.issue(cycle)


##############################################################################################################################################
###Branch prediction
### modify issue here, the check of branch instrs is the same as Add, but the rename is different
    if("Bne" in instr.type) or ("Beq" in instr.type):
        logging.info("cycle{}-issue():trying to issue a branch instr({})".format(cycle,instr.__str__()))
        #instead of find dependency of operand 2 and 3, we do that with operand 1 and 2
        ###begin renaming operand 1
        if(not isinstance(instr.operand1, str)):#immediate number
            operand1 = instr.operand1
        else:#operand2 is R<> OR F<>
            operand1 = registerAliasTable.get_alias(instr.operand1)
            if ('ROB' in operand1):
                temp = reorderBuffer.get_value(operand1)
            
                if not temp == None:# The result isn't calculated. Return and wait for at least one cycle
                    operand1 = temp
            else:
                operand1 = architecturalRegisterFile.get_value(operand1)
            if operand1 == None:#Must be a mistake, because ARF must have values.
                logging.error('ARF does not have correct value')
                raise Exception

        ### begin renaming operand 2
        if(not isinstance(instr.operand2, str)):#immediate number
            operand2 = instr.operand2
        else:#operand2 is R<> OR F<>
            operand2 = registerAliasTable.get_alias(instr.operand2)
            if ('ROB' in operand2):
                temp = reorderBuffer.get_value(operand2)
            
                if not temp == None:# The result isn't calculated. Return and wait for at least one cycle
                    operand2 = temp
            else:
                operand2 = architecturalRegisterFile.get_value(operand2)
            if operand2 == None:#Must be a mistake, because ARF must have values.
                logging.error('ARF does not have correct value')
                raise Exception
            
        # we still utilize a ROB entry, but we don't rename in RAT
        rob_name = reorderBuffer.issue_push(instr)
        logging.info("cycle{}:issue: assign({}) to instr{}".format(cycle,rob_name,instr.__str__()))
        instr.issue = cycle
        ##Write to RS, however the operand should be changed
        logging.info("cycle{}:issue: loading instr to ({},{})".format(cycle,c_id,idx))
        reservationStations.load(c_id, idx, instr, rob_name, operand1, operand2)
        ##change the branch unit info
        branchUnit.block_fetch = False
        branchUnit.in_prediction = True
        #make prediction
        branchUnit.make_prediction(instr)
        #change the pc base on prediction results
        if(branchUnit.strategy == True):#branch
            instructionQueue.pc = int(branchUnit.addr_branch)
        else:
            instructionQueue.pc = int(branchUnit.addr_nbranch)
        logging.warning("cycle{}:issue: branch prediction of {} made! pc changed from {} to {}".format(cycle,branchUnit.strategy,instr.addr,instructionQueue.pc))
        return


    ##Finish pop the instr and alias the result operand, begin renaming operand 2
    if(not isinstance(instr.operand2, str)):#immediate number
        operand2 = instr.operand2
    else:#operand2 is R<> OR F<>
        operand2 = registerAliasTable.get_alias(instr.operand2)
        if ('ROB' in operand2):
            temp = reorderBuffer.get_value(operand2)
            
            if not temp == None:# The result isn't calculated. Return and wait for at least one cycle
                operand2 = temp
        else:
            operand2 = architecturalRegisterFile.get_value(operand2)
            if operand2 == None:#Must be a mistake, because ARF must have values.
                logging.error('ARF does not have correct value')
                raise Exception
            
    ##Finish pop the instr and alias the result operand, begin renaming operand 3
    if(not isinstance(instr.operand3, str)):#immediate number
        operand3 = instr.operand3
    else:#operand3 is R<> OR F<>
        operand3 = registerAliasTable.get_alias(instr.operand3)
        if ('ROB' in operand3):
            temp = reorderBuffer.get_value(operand3)
            
            if not temp == None:# The result isn't calculated. Return and wait for at least one cycle
                operand3 = temp
        else:
            operand3 = architecturalRegisterFile.get_value(operand3)
            if operand3 == None:#Must be a mistake, because ARF must have values.
                logging.error('ARF does not have correct value')
                print(architecturalRegisterFile)
                raise Exception
            
    ##chek type of operand2 & operand3
    if (not isinstance(operand2, (int, float, str))):
        logging.error('operand2 is not a value!')
        raise Exception
    if (not isinstance(operand3, (int, float, str))):
        logging.error('operand3 is not a value!')
        raise Exception
    
    #Rename operand1
    rob_name = reorderBuffer.issue_push(instr)
    logging.info("cycle{}:issue: assign({}) to instr{}".format(cycle,rob_name,instr.__str__()))
    if(instr.operand1 != "R0"):#NOP handle + R0 handle
        registerAliasTable.rename(instr.operand1, rob_name)
    """
    ROB: 'ROB<i>'|value...
	RAT: 'R<i>'/'F<i>'|'R<i>'/'F<i>'/'ROB<i>'
	ARF: 'R<i>'/'F<i>'| value
    """

    instr.issue = cycle
    ##Write to RS
    logging.info("cycle{}:issue: loading instr to ({},{})".format(cycle,c_id,idx))
    reservationStations.load(c_id, idx, instr, rob_name, operand2, operand3)
    # logging.info("RS:\n"+ reservationStations.__str__())




    