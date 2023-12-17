"""
Processing units
stages take part in:
 - execute
 - write back

Processing units will have 3 independent clusters --> PU_cluster
 - Int processer
 - FP adder
 - FP multiplier

a cluster will have multiple independent PUs --> PU, which relies on a PU_config class

The CDB will also be implicitly implemented in the PUs:
current arbiter rule:
 1.instr in a single PU's buffer: FIFO
 2.instr in multi PUs in a cluster: Round piority (1st round: 1-->n; 2nd round: 2-->1; 3rt round: 3-->2,...)
 3.instr in multi cluseter: round piority
 4.sequence: choose a cluster --> choose a PU --> PU pops the instr
"""
from Instruction import Instruction
import logging
"""
PU_config will be responsible for
 - keep the computation methods for each instr(however special methods may not included)
 - keep the computation latency for each instr(with a default value)
 - PU config should only be modified at initialization 
"""
class PU_config:
    # basic computation methods
    def nop( operand1, operand2):
        return 1
    def add( operand1, operand2):
        return operand1 + operand2
    def sub( operand1, operand2):
        return operand1 - operand2
    def multiply( operand1, operand2):
        return operand1 * operand2
    def devide( operand1, operand2):
        assert operand2 != 0, "Runtime ERROR: devided by 0"
        return operand1 / operand2
    #Branch prediction: add more processing methods for Bne and Beq
    def equal(operand1, operand2):
        return operand1 == operand2
    def nequal(operand1, operand2):
        return operand1 != operand2
    __latency = {#default latency config
        "NOP":1,
        # "Beq":3,
        # "Bne":3,
        "ADD":2,
        "ADDI":2,
        "SUB":2,
        "SUBI":2,
        "MULTII":4,
        "ADDD":3,
        "SUBD":3,
        "MULTID":10,
        "DEVIDED":20
    }
    __compute = {}
    def __init__(self, latency_configs={}, compute_configs={}) -> None:
        #init latency configs --> latency config should be dict{instr:latency}
        for instr in latency_configs:
            self.__latency[instr] = latency_configs[instr]
        #init compute configs --> compute config should be dict{instr:func} the func should take (operand1, operand2) as params
        #init default configs
        self.__compute["NOP"] = PU_config.nop
        self.__compute["ADD"] = PU_config.add
        self.__compute["ADDI"] = PU_config.add
        self.__compute["SUB"] = PU_config.sub
        self.__compute["SUBI"] = PU_config.sub
        self.__compute["MULTII"] = PU_config.multiply
        self.__compute["ADDD"] = PU_config.add
        self.__compute["SUBD"] = PU_config.sub
        self.__compute["MULTID"] = PU_config.multiply
        self.__compute["DEVIDED"] = PU_config.devide
        #init modified configs
        for instr in compute_configs:
            self.__compute[instr] = compute_configs[instr]
        #check 
        for instr in self.__latency:
            assert instr in self.__compute, "PU_config.__init__():{} is in __latency but not in __compute".format(instr)
        for instr in self.__compute:
            assert instr in self.__latency, "PU_config.__init__():{} is in __compute but not in __latency".format(instr)

    def get_latency(self,instr):
        if isinstance(instr, Instruction):
            instr_name = instr.type
        elif isinstance(instr,str):
            instr_name = instr
        else:
            raise Exception("PU_config.get_latency(): invalidparam type:{}".format(instr))
        assert instr_name in self.__latency, "PU_config.get_latency(): instr type doesn't exist:{}".format(instr_name)
        return self.__latency[instr]
    
    def compute(self,instr):
        if isinstance(instr, Instruction):
            instr_name = instr.type
        elif isinstance(instr,str):
            instr_name = instr
        else:
            raise Exception("PU_config.compute(): invalidparam type:{}".format(instr))
        assert instr_name in self.__latency, "PU_config.compute(): instr type doesn't exist:{}".format(instr_name)
        return self.__compute[instr]
 
"""
a PU will be the basic element for computation
attributes:
    - type
    - target
    - target_value
    - value1
    - value2
    - instr
    - occupied_flag

    - exec_counter #record how many cycles current instr has been executed
    - config: PU_config for exec support

    - instr_buffer #store the instrs finished exec, but not written back by cdb
    - buffer_size
For ease of implementation, the PU is unified for all clusters, i.e. a PU, wherever it is, can execute all 
this will be implemented using the PU_config class
"""
class PU:
    def __init__(self,buffer_size,config = PU_config()) -> None:#if not specified, will use default PU config
        ###
        #space for store instrs
        self.type =None
        self.target =None
        self.target_value = None
        self.value1 = None
        self.value2 = None
        self.instr = None
        self.occupied_flag = False
        ###
        #exec configs
        self.exec_counter = None
        self.config = config
        ###
        #local bufffering 
        self.instr_buffer = []
        self.buffer_size = buffer_size

    def __str__(self) -> str:
        str_ = ""
        #PU part
        str_ += "[PU]:"
        if(self.occupied_flag):
            str_ += str(self.type) + "\t"
            str_ += str(self.target) + "\t"
            str_ += str(self.value1) + "\t"
            str_ += str(self.value2 )+ "\t"
            str_ += str(self.target_value) + "\t"
            str_ += str(self.exec_counter) + "/" +str(self.config.get_latency(self.type)) +"\t"
        else:
            str_ += "<empty>\t"
        str_ += "| [buffer]:"
        if(len(self.instr_buffer)>0):
            for output in self.instr_buffer:
                str_ += str(output["target"]) +" "+ str(output["target_value"]) + "|\t"
        else:
            str_ += "<empty>\t"
        return str_
        
    def clean_instr(self): #clean the instr related part, the config and buffer not changed
        ###
        #space for store instrs
        self.type =None
        self.target =None
        self.target_value = None
        self.value1 = None
        self.value2 = None
        self.instr = None
        self.occupied_flag = False
        self.exec_counter = None

    def clean_all(self): #clean the instr and buffer related part, the config not changed
        self.clean_instr()
        self.instr_buffer.clear()

    def check_occupied(self):
        return self.occupied_flag
    
    def check_execute_ready(self): #when the counter value is larger than what registerd in the config, the instr will be regarded as ready
        if not self.check_occupied():
            return False
        return self.exec_counter >= self.config.get_latency(self.type)

    def check_offload_ready(self): #we only offload from the buffer, if it has items, it's ready
        return len(self.instr_buffer) > 0

    def load(self, info):#the info should be a dict with {"type", "target","value1","value2","instr"}
        #check the info 
        assert self.occupied_flag == False, "PU.load():trying to load in an occupied PU"
        for attr in ["type", "target","value1","value2","instr"]:
            assert attr in info, "PU.load(): invalid input format, require:{}".format(attr)
        #load attrs
        self.type = info["type"]
        self.target = info["target"]
        self.value1 = info["value1"]
        self.value2 = info["value2"]
        self.instr = info["instr"]

        #set flags
        self.exec_counter = -1# after first exec() will be 0
        self.occupied_flag = True

        #do computation immediately
        """TODO: add branch here"""
        self.target_value = self.config.compute(self.type)(self.value1,self.value2)

    def local_buffer(self): #move current instr to the local buffer
        #store the info
        info = {}
        info["type"] = self.type
        info["target"] = self.target
        info["target_value"] = self.target_value
        info["instr"] = self.instr
        self.instr_buffer.append(info)
        #reset the PU for following instrs
        self.clean_instr()

    def execute(self):
        '''For ease of implementation, all instrs will be sent to the buffer immediately'''
        """TODO: add branch here"""
        if(not self.check_occupied()):#if the PU is empty, the we do nothing
            return
        #increase the counter
        self.exec_counter += 1

        #check if ready to go to buffer
        if self.check_execute_ready():
            #check if there's space in the buffer
            if len(self.instr_buffer) < self.buffer_size:
                self.local_buffer()

    def offload(self):
        '''we only offload from the buffer
            which means for a empty buffer, the instr can 1.go to buffer;2 writeback in one single cycle'''
        assert self.check_offload_ready(), "PU.offload():trying to offload an unready PU"
        ret_ = self.instr_buffer[0]
        del self.instr_buffer[0]
        #if the PU has a ready instr, it will be buffered immediately
        if(self.check_execute_ready()):
            self.local_buffer()
        return ret_

"""
A PU_cluster will manage a group of PUs of the same type, it will responsible for
 - type management
 - find available place
 - write_back_arbiter

A PU_cluster will have the following attributes
    - a list of accepted instr types
    - size
    - a list of PUs
    - a name, will be correspond to the name of a RS_cluster
"""

class PU_Cluster:
    def __init__(self,name,instr_list,size,buffer_size,config = PU_config()) -> None:
        self.name = name
        self.instr_list = instr_list
        self.size = size
        self.PUs = []
        for i in range(size):
            self.PUs.append(PU(buffer_size,config))
        self.arbit_ptr = 0

    def __str__(self) -> str:
        str_ = ""
        str_ += "*****"+str(self.name)+"*****\n"
        for i in range(self.size):
            str_+=self.PUs[i].__str__()+"\n"
        return str_
    
    def check_empty_entry(self): #find a empty entry for load, if not found, return -1
        for i in range(self.size):
            if not self.PUs[i].check_occupied():
                return i
        return -1
    
    def increase_ptr(self,i):
        assert i < self.size, "PU_Cluster({}).increase_ptr(): index {} out of range {}".format(self.name,i,self.size)
        i += 1
        if i >= self.size:
            i = 0
        return i

    def check_ready_entry(self): #find a empty entry for off load, if not found, return -1, will begin at the self.arbit_ptr to realize fairness
        i = self.increase_ptr(self.arbit_ptr)        
        while(1):
            #check availability 
            if self.PUs[i].check_offload_ready():
                self.arbit_ptr = self.increase_ptr(self.arbit_ptr)#whether find or not, next time we will begin at a later idx
                return i
            if(i == self.arbit_ptr):
                break
            i = self.increase_ptr(i)
        #whether find or not, next time we will begin at a later idx
        self.arbit_ptr = self.increase_ptr(self.arbit_ptr)
        return -1
    
    def load(self,idx:int, info):
        assert "type" in info, "PU_Cluster.load(): invalid param format"
        assert info["type"] in self.instr_list, "PU_Cluster.load(): invalid input type, given{}, allow{}".format(info["type"],self.instr_list)
        assert idx < self.size, "PU_Cluster.load():index{} of of range{}".format(idx,self.size)
        self.PUs[idx].load(info)

    def execute(self):
        for PU in self.PUs:
            PU.execute()
    
    def offload(self,idx,cycle):
        assert self.PUs[idx]
        assert idx < self.size, "PU_Cluster.offload():index{} of of range{}".format(idx,self.size)
        ret = self.PUs[idx].offload()
        ret["instr"].writeback = cycle
        return ret

"""
A ProcessingUnits have several different clusters
will use a dict to kep the entries
"""        

class ProcessingUnits:
    def __init__(self, configs:list) -> None:
        '''configs will be a list of dicts, each contains the config needed by a PU_cluster: {name,instr_list,size,buffer_size,config = PU_config()}'''
        #check the configs
        assert isinstance(configs,list), "ProcessingUnits.__init__(): invalid param format, need a list, get a {}".format(type(configs))
        for config in configs:
            assert isinstance(config, dict), "ProcessingUnits.__init__(): invalid unit in the list, need a dict, get a {}".format(type(config))
            for attr in ["name","instr_list","size","buffer_size","config"]:
                assert attr in config, "ProcessingUnits.__init__(): invalid unit in the list, need attr {}".format(attr)

        #init clusters
        self.PU_clusters = {}
        for config in configs:
            self.PU_clusters[config["name"]] = PU_Cluster(config["name"],config["instr_list"],config["size"],config["buffer_size"],config["config"])

        self.keys = []
        for config in configs:
            self.keys.append(config["name"])

        self.arbit_ptr = 0

    def increase_ptr(self,i):
        assert i < len(self.keys), "ProcessingUnits.increase_ptr(): index {} out of range {}".format(i,len(self.keys))
        i +=1 
        if i >= len(self.keys):
            i = 0
        return i
    
    def __str__(self) -> str:
        str_ = ""
        str_ += "-----"+"ProcessingUnits"+"-----\n"
        for cluster_id in self.PU_clusters:
            str_ += self.PU_clusters[cluster_id].__str__() + "\n"
        return str_

    def check_instr_name(self,instr):#
        '''check the type of given instrution, return cluster_id or None if not found'''
        if isinstance(instr,Instruction):
            instr_name = instr.type
        elif isinstance(instr,str):
            instr_name = instr
        else:
            logging.error("ReservationStations.check_instr_name():{} is invalid format".format(instr))
        for c_id in self.PU_clusters:
            if instr_name in self.PU_clusters[c_id].instr_list:
                return c_id
        return None

    def check_empty_entry(self,cluster_id):
        """ check if the cluster of given cid has empty entry
            return the entry idx if found, -1 if not found
        """
        assert cluster_id in self.PU_clusters, "ProcessingUnits.check_empty_entry(): invalid cluster_id, allowed{}, given{}".format(self.PU_clusters.keys, cluster_id)
        return self.PU_clusters[cluster_id].check_empty_entry()
    
    def check_ready_entry(self):#
        '''get a (c_id, idx) which is ready to offload, return None when not find'''
        i = self.increase_ptr(self.arbit_ptr)
        while(1):
            c_id = self.keys[i]
            idx = self.PU_clusters[c_id].check_ready_entry()
            # logging.info("checking cluster({}), get({})".format(c_id,idx))
            if idx != -1:
                self.arbit_ptr = self.increase_ptr(self.arbit_ptr)
                return (c_id,idx)
            if(i == self.arbit_ptr):
                break
            i = self.increase_ptr(i)
        self.arbit_ptr = self.increase_ptr(self.arbit_ptr)
        return (None,None)
        
    def load(self, cluster_id, idx, info):
        '''load the given informantion to the (cid,idx) entry
            input: cid, idx, info:{"type","target","value1","value2","instr"}
        '''
        assert cluster_id in self.PU_clusters, "ProcessingUnits.load(): invalid cluster_id, allowed{}, given{}".format(self.PU_clusters.keys, cluster_id)
        self.PU_clusters[cluster_id].load(idx,info)

    def execute(self):
        "automatically execute all PUs"
        for cluster in self.PU_clusters:
            self.PU_clusters[cluster].execute()
    
    def offload(self, cluster_id, idx, cycle):
        """ offload an instr from the buffer in (cid,idx)
            return value:{"type","target","target_value","instr"}
        """
        assert cluster_id in self.PU_clusters, "ProcessingUnits.offload(): invalid cluster_id, allowed{}, given{}".format(self.PU_clusters.keys, cluster_id)
        return self.PU_clusters[cluster_id].offload(idx,cycle)
        




if __name__ == "__main__":
    # # test code for PU config
    # config = PU_config()
    # print(config.get_latency("DEVIDED"))
    # print(config.compute("ADDI")(3,5))
    # # test code for PU
    # pu = PU(2)
    # for cycle in range(30):
    #     #try to load
    #     print("##########cycle:{}##########".format(cycle))
    #     if not pu.check_occupied():
    #         pu.load({"type":"ADDI","target":"ROB{}".format(cycle+2),"value1":cycle*3,"value2":cycle+2,"instr":Instruction("ADDI","R6","R7","R8")})
    #     pu.execute()
    #     if(cycle > 27):
    #         if pu.check_offload_ready():
    #             result = pu.offload()
    #             print("offloading:",result)
    #     print(pu)
    # # test code for PU cluster
    # puc = PU_Cluster("Test",["ADDI","SUBI"],5,2)
    # print(puc)
    # for cycle in range(40):
    #     #try to load
    #     print("##########cycle:{}##########".format(cycle))
    #     idx = puc.check_empty_entry()
    #     if idx != -1:
    #         print("load instr to entry {}".format(idx))
    #         puc.load(idx,{"type":"ADDI","target":"ROB{}".format(cycle+2),"value1":cycle*3,"value2":cycle+2,"instr":Instruction("ADDI","R6","R7","R8")})
        
    #     puc.execute()
    #     if(cycle > 30):
    #         idx = puc.check_ready_entry()
    #         if idx != -1:
    #             info = puc.offload(idx,cycle)
    #             print("offload instr:", info, "on idx {}".format(idx))
        
    #     print(puc)
    # test code for PUs
    config = PU_config()
    I_con = {"name":"Int", "instr_list":["ADDI","SUBI"],"size":5,"buffer_size":2,"config":config}
    F_con = {"name":"Float", "instr_list":["ADDD","SUBD"],"size":5,"buffer_size":2,"config":config}
    pus = ProcessingUnits([I_con,F_con])
    print(pus)
    for cycle in range(40):
        print("##########cycle:{}##########".format(cycle))
        instr1 = Instruction("ADDI","R6","R7","R8")
        instr2 = Instruction("ADDD","R6","R7","R8")
        cid = pus.check_instr_name(instr1)
        if cid != None:
            idx = pus.check_empty_entry(cid)
            if(idx != -1):
                pus.load(cid, idx, {"type":"ADDI","target":"ROB{}".format(cycle+2),"value1":cycle*3,"value2":cycle+2,"instr":instr1})
                print("load in {}, {}".format(cid,idx))
        cid = pus.check_instr_name(instr2)
        if cid != None:
            idx = pus.check_empty_entry(cid)
            if(idx != -1):
                pus.load(cid, idx, {"type":"ADDD","target":"ROB{}".format(cycle+2),"value1":cycle*3,"value2":cycle+2,"instr":instr2})
                print("load in {}, {}".format(cid,idx))
        pus.execute()

        if cycle > 30:
            cid, idx = pus.check_ready_entry()
            if cid != None:
                info = pus.offload(cid,idx,cycle)
                print("offload: ", info, "at {},{}".format(cid,idx))
        print(pus)

        


            