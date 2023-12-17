"""
Some components may need some extra operations at the end of one cycle

- InstrQueue
- RS
- ROB
"""
from InstructionQueue import InstructionQueue
from ReservationStations import ReservationStations
from ReorderBuffer import ReorderBuffer
from MemoryUnit_New import MemoryUnit
def Update(instructionQueue:InstructionQueue,reservationStations:ReservationStations,reorderBuffer:ReorderBuffer,memoryUnit:MemoryUnit):
    instructionQueue.update()
    reservationStations.update()
    reorderBuffer.update()
    memoryUnit.update()