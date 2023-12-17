"""
branch prediction and roll back 
"""
from Instruction import Instruction
"""
FSM: base of branch predictor
"""
class FSM:
    def __init__(self,inputs:list,states:list,outputs:dict,change_tbl:dict,init_state) -> None:
        """
        inputs:[<possible inputs>]
        states:[<possible states>]
        outputs:{state:output}
        change_tbl{ state:{input:state}  }
        """
        #check correctness
        #1.all state should have output
        for state in states:
            assert state in outputs
        #2.all state should have change of all different inputs
        for state in states:
            assert state in change_tbl
            for input in inputs:
                assert input in change_tbl[state]
                assert change_tbl[state][input] in states
        self.inputs = inputs
        self.outputs = outputs
        self.states = states
        self.change_tbl = change_tbl
        self.state = init_state
    def output(self):
        return self.outputs[self.state]
    def update_status(self,input):
        assert input in self.inputs
        self.state = self.change_tbl[self.state][input]
    
class BranchPredictor:
    def __init__(self):
        """False: no branch, true: branch"""
        self.predictors = []
        for i in range(8):
            self.predictors.append(FSM(inputs = [False, True],
                                       states = ["predictFalse","predictTrue"],
                                       outputs = {"predictFalse":False,"predictTrue":True},
                                       change_tbl = {
                                                    "predictFalse":{False:"predictFalse",True:"predictTrue"},
                                                    "predictTrue":{False:"predictFalse",True:"predictTrue"}},
                                        init_state= "predictFalse"))
    def __get_idx(self,instr_info):
        if isinstance(instr_info, Instruction):
            addr = instr_info.addr%8
        if isinstance(instr_info, int):
            addr = instr_info%8
        return addr

    def predict(self,instr_info):
        return self.predictors[self.__get_idx(instr_info)].output()
    def update_status(self,instr_info,result:bool):
        self.predictors[self.__get_idx(instr_info)].update_status(result)

"""
class BranchPredictorv2:
    def __init__(self) -> None:
        self.predictors = []
        self.targets=[]
        self.size = 4
        for i in range(self.size):
            self.predictors.append(False)
            self.targets.append(0)
    def __get_idx(self,instr_info):
        if isinstance(instr_info, Instruction):
            idx = instr_info.addr%4
        if isinstance(instr_info, int):
            idx = instr_info%4
        return idx
    def predict(self,instr_info):
        return self.predictors[self.__get_idx(instr_info)]
    def get_tgt(self,instr_info):
        return self.targets[self.__get_idx(instr_info)]
    def update_status(self,instr_info,result:bool):
        self.predictors[self.__get_idx(instr_info)] = result
    def update_target(self,instr_info,target_value):
        self.targets[self.__get_idx(instr_info)] = target_value%8
    def __str__(self):
        str_="*****branch predictor*****\nidx\tpred\ttgt\t\n"
        for i in range(self.size):
            str_ += "{}\t{}\t{}\t\n".format(i,self.predictors[i],self.targets[i])
        return str_ 
        
class BranchUnit:
    def __init__(self) -> None:
        self.predictor = BranchPredictorv2()
        self.block_fetch = False
        self.in_prediction = False
        self.addr = None
        self.addr_branch = None
        self.addr_branch_real = None
        self.addr_nbranch = None
        self.strategy = None# True:branch, False:no branch
        self.snapshots = {}

        self.snapshot_signal = False
        self.roll_back_signal = False
    def __str__(self) -> str:
        return self.predictor.__str__()
    def make_prediction(self,instr:Instruction):
        #record 2 paths of this instr
        self.addr = instr.addr
        self.addr_branch = (instr.addr+1) - (instr.addr+1)%8 + self.predictor.get_tgt(instr.addr)
        self.addr_branch_real = instr.addr+1 + instr.operand3
        self.addr_nbranch = instr.addr + 1
        #make prediction
        self.strategy = self.predictor.predict(instr)
        #prepare to do snapshot
        self.snapshot_signal = True
        
    # def take_snapshots():
    #  will be in main()
    def check_misprediction(self,result):
        if self.strategy != result:
            print("stragy:",self.strategy)
            print("result:",result)
            return True
        if self.strategy == True and self.addr_branch != self.addr_branch_real:
            print("pred_tgt:",self.addr_branch)
            print("real_tgt:",self.addr_branch_real)
            return True
        return False
    # the backroll will be directly inplemented in main
    def clean(self):
        predictor = self.predictor
        self.__init__()
        self.predictor = predictor
"""         

class BranchPredictorv2:
    def __init__(self) -> None:
        self.predictors = []
        self.targets=[]
        self.size = 8
        for i in range(self.size):
            self.predictors.append(False)
            self.targets.append(0)
    def __get_idx(self,instr_info):
        if isinstance(instr_info, Instruction):
            idx = instr_info.addr%8
        if isinstance(instr_info, int):
            idx = instr_info%8
        return idx
    def predict(self,instr_info):
        return self.predictors[self.__get_idx(instr_info)]
    def get_tgt(self,instr_info):
        return self.targets[self.__get_idx(instr_info)]
    def update_status(self,instr_info,result:bool):
        self.predictors[self.__get_idx(instr_info)] = result
    def update_target(self,instr_info,target_value):
        self.targets[self.__get_idx(instr_info)] = target_value%8
    def __str__(self):
        str_="*****branch predictor*****\nidx\tpred\ttgt\t\n"
        for i in range(self.size):
            str_ += "{}\t{}\t{}\t\n".format(i,self.predictors[i],self.targets[i])
        return str_ 
        
class BranchUnit:
    def __init__(self) -> None:
        self.predictor = BranchPredictorv2()
        self.block_fetch = False
        self.in_prediction = False
        self.addr = None
        self.addr_branch = None
        self.addr_branch_real = None
        self.addr_nbranch = None
        self.strategy = None# True:branch, False:no branch
        self.snapshots = {}

        self.snapshot_signal = False
        self.roll_back_signal = False
    def __str__(self) -> str:
        return self.predictor.__str__()
    def make_prediction(self,instr:Instruction):
        #record 2 paths of this instr
        self.addr = instr.addr
        # self.addr_branch = (instr.addr+1) - (instr.addr+1)%8 + self.predictor.get_tgt(instr.addr)
        self.addr_branch_real = instr.addr+1 + instr.operand3
        self.addr_branch= self.addr_branch_real
        self.addr_nbranch = instr.addr + 1
        #make prediction
        self.strategy = self.predictor.predict(instr)
        #prepare to do snapshot
        self.snapshot_signal = True
        
    # def take_snapshots():
    #  will be in main()
    def check_misprediction(self,result):
        if self.strategy != result:
            print("stragy:",self.strategy)
            print("result:",result)
            return True
        if self.strategy == True and self.addr_branch != self.addr_branch_real:
            print("pred_tgt:",self.addr_branch)
            print("real_tgt:",self.addr_branch_real)
            return True
        return False
    # the backroll will be directly inplemented in main
    def clean(self):
        predictor = self.predictor
        self.__init__()
        self.predictor = predictor
     



if __name__ == "__main__":
    # # testcode for FSM:
    # inputs = [False, True]
    # states = ["predictFalse","predictTrue"]
    # outputs = {"predictFalse":False,"predictTrue":True}
    # change_tbl = {
    #     "predictFalse":{False:"predictFalse",True:"predictTrue"},
    #     "predictTrue":{False:"predictFalse",True:"predictTrue"}
    # }
    # fsm = FSM(inputs,states,outputs,change_tbl,"predictTrue")
    # print(fsm.output())
    # fsm.update_status(False)
    # print(fsm.output())
    # fsm.update_status(False)
    # print(fsm.output())
    # fsm.update_status(True)
    # print(fsm.output())
    # test code for branch predictor
    bp = BranchPredictor()
    print(bp.predict(4))
    bp.update_status(4,True)
    print(bp.predict(4))
    Instr = Instruction("Bne","A1","A2","-20")
    Instr.addr = 7
    print(bp.predict(Instr))
    bp.update_status(Instr,True)
    print(bp.predict(Instr))
    
