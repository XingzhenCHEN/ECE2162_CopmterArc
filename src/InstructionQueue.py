"""
The Instr Queue: beginging of the pipeline
- need to fetch from the instr memory
- need to issue to the ROB, RAT, RS
"""
from queue import Queue
import copy
class InstructionQueue:
    def __init__(self,size=10) -> None:
        self._maxsize = size
        self._instrlist = Queue(size)
        self._flaglist = Queue(size)#False: this entry is just from Mem, will be ready in next cycle
        self.pc = 0
        self.instr_length = 1

    def __str__(self):
        str_ = ""
        str_ += "\n-----InstrQueue-----\n"
        str_ += "pc:"+str(self.pc)+"\n"
        str_ += "status|instrs:\n"
        for i in range(self._instrlist.qsize()):
            str_ += str(self._flaglist.queue[i]) + "|\t" + self._instrlist.queue[i].__str__() + "\n"
        return str_

    def _enqueue(self,instr):
        '''join one instr'''
        self._instrlist.put(instr)
        self._flaglist.put(False)

    def _dequeue(self):#
        '''pop out one instr'''
        instr = self._instrlist.get()
        self._flaglist.get()
        return instr

    def touch(self):
        '''touch for issue stage'''
        return copy.deepcopy(self._instrlist.queue[0])

    def check_full(self):#
        '''check if there's empty zoom'''
        return self._instrlist.full()
    
    def check_empty(self):#
        '''if there's no instrs or if the instr is not ready, we regard the queue as empty'''
        if self._instrlist.empty():
            return True
        else:
            return not self._flaglist.queue[0]
    
    def fetch(self,instr): #
        '''get an instr, store at queue, and also increase the pc'''
        if self.check_full():
            raise Exception("InstructionQueue.fetch: trying to fetch when the queue is full")
        self._enqueue(instr)
        self.pc += self.instr_length

    def update(self):#
        '''update the flags at the end of each cycle, to make sure the timing is correct(an instr won't be fetched and issued at the same cycle)'''
        for i in range(self._instrlist.qsize()):
            self._flaglist.queue[i] = True
    
    def issue(self,cycle): #issue an instr 
        if self.check_empty():
            raise Exception("InstructionQueue.issue: trying to issue when the queue is empty")
        instr = self._dequeue()
        instr.issue = cycle
        return instr
    