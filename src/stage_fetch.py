"""
components:
InstructionMemory,InstructionQueue

tasks
"""
import logging
from InstructionMemory import InstructionMemory
from InstructionQueue import InstructionQueue
from BranchUnit import BranchUnit
from output import OutputHandler_fetch
def Fetch(instructionMemory:InstructionMemory, instructionQueue:InstructionQueue, branchUnit:BranchUnit,outputHandler_fetch:OutputHandler_fetch ,cycle)->None:
    #branch prediction
    #check the branchUnit and then decide fetch or not
    if branchUnit.block_fetch:
        logging.info("cycle{}-fetch():fetch nothing since branch prediction haven't been made".format(cycle))
        return
    #get current program counter
    pc = instructionQueue.pc 
    #check memory: if the pc is not valid for the memory, we return
    if not instructionMemory.check_valid(pc):
        logging.warning("cycle{}-fetch: invalid address".format(cycle))
        return
    #check Queue: if the queue is full, we return
    if instructionQueue.check_full():
        logging.info("cycle{}-fetch: instructionQueue is full ".format(cycle))
        return
    #safely get a instr from the memory...
    instr = instructionMemory.fetch(pc)
    #branch prediction
    #if we are already in a prediction, and trying to fetch another one, things will be dangerous since the block of second branch will be cancelled by the return of first one
    if ("Bne" in instr.type) or ("Beq" in instr.type):
        if(branchUnit.in_prediction):
            logging.info("cycle{}-fetch(): fetch blocked since since we don't fetch the second branch instr when the first one is still in prediction".format(cycle))
            return
    #... and push into the queue
    instructionQueue.fetch(instr)
    outputHandler_fetch.get_instr(instr)
    logging.warning("cycle{}-fetch: fetch instruction:\t".format(cycle)+instr.__str__()+"\tin pc:{}".format(pc))
    
    #branch prediction
    # if we fetched a branch, we should wait until the prediction is made
    if 'Bne' in instr.type or 'Beq' in instr.type:
        logging.warning("cycle{}-fetch():fetch will be blocked due to this branch instr".format(cycle))
        branchUnit.block_fetch = True
