"""
Reservation Stations
stages taking part in
    - issue(renaming)
    - execute(check and pop out instrs)
    - writeback(renaming)

3 kind of architectures --> 3 RS_Cluster s 
    - int FU
    - FP adder
    - FP multiplier

each cluster will have multiple entries  --> N RS_Entry
"""
from Instruction import Instruction
import copy
import logging

"""
A RS_Entry will have following attributes
    - type
    - target
    - value1
    - value2
    - tag1
    - tag2
    - ready_flag (for 1-cycle latency after loaded)

A entry is only responsible for 
- 1. load an instr, without type checking
- 2. offload an instr, without type checking
- 3. re-write tag with given value
- 4. status checking
"""
class RS_Entry:
    def __init__(self) -> None:
        self._type = None
        self._target = None
        self._value1 = None
        self._value2 = None
        self._tag1 = None
        self._tag2 = None
        self._instr = None
        self.ready_flag = False
        self._occupy_flag = False

    def __str__(self):
        str_ = ""
        if self._occupy_flag:
            str_ += str(self._type) + "\t"
            str_ += str(self._target) + "\t"
            str_ += str(self._value1) + "\t"
            str_ += str(self._value2) + "\t"
            str_ += str(self._tag1) + "\t"
            str_ += str(self._tag2) + "\t"
            if self.ready_flag:
                str_ += "ready"
            else:
                str_ += "unready"
        else:
            str_ += "<empty>"
        return str_

    def _write(self, instr:Instruction, target:str, operand1, operand2):
        self._type = instr.type
        #make sure the target is a ROB entry
        if not ("ROB" in target):
            logging.error(("RS_Entry.load: target is not ROB entry, target:"+ str(target)))
            raise Exception(("RS_Entry.load: target is not ROB entry"))
        #check tags and values are legal
        if isinstance(operand1,str):
            if not ("ROB" in operand1):
                logging.error(("RS_Entry.load: target is not operand1 , operand1:"+ str(operand1)))
                raise Exception(("RS_Entry.load: operand is not ROB entry"))
        if isinstance(operand2,str):
            if not ("ROB" in operand2):
                logging.error(("RS_Entry.load: target is not operand2 , operand2:"+ str(operand2)))
                raise Exception(("RS_Entry.load: operand is not ROB entry"))
        #load target
        self._target = target
        #load operand
        if isinstance(operand1,str):#operand1 is ROB entry
            self._tag1 = operand1
        else:
            self._value1 = operand1
        if isinstance(operand2,str):#operand1 is ROB entry
            self._tag2 = operand2
        else:
            self._value2 = operand2
        #load other things
        self._instr = instr
        self.ready_flag = False
        self._occupy_flag = True

    def clean(self):
        self.__init__()

    def check_occupied(self):# check if the entry is occupied
        return self._occupy_flag
    
    def check_ready(self):# check if the entry is ready for execute
        if not self._occupy_flag:
            return False
        if not self.ready_flag:
            return False #even if the entry is all of immediate numbers, it should wait for 1 cycle
        if self._value1 == None:
            return False
        if self._value2 == None:
            return False
        return True
    
    def load(self, instr:Instruction, target:str, operand1, operand2):
        if self.check_occupied():
            logging.error("RS_Entry.load():trying to load to an occupied entry, current entry:" + self.__str__())
            raise Exception("RS_Entry.load():trying to load to an occupied entry")
        self._write(instr,target,operand1,operand2)

    def offload(self):# output the needed data in form of dict
        if not self.check_ready():
            logging.error("RS_Entry.offload(): trying to offload with entry unready, current entry:" + self.__str__())
            raise Exception("RS_Entry.offload(): trying to offload with entry unready")
        ret_ = {}
        ret_["type"] = self._type
        ret_["target"] = self._target
        ret_["value1"] = self._value1
        ret_["value2"] = self._value2
        ret_["instr"] = self._instr

        #clean the entry
        self.clean()
        return ret_

    def write_back(self,tag:str,value):
        if self._tag1 == tag:#check if operand1 contains the tag
            self._tag1 = None
            self._value1 = value
        if self._tag2 == tag:
            self._tag2 = None
            self._value2 = value

    def update(self):
        if not self.check_occupied():#only when the
            return
        else:
            self.ready_flag = True
"""
A RS_cluster will have the following attributes
    - a list of accepted instr types
    - size
    - a list of RS_entries

"""   
class RS_Cluster:
    def __init__(self,name,instr_list,size) -> None:
        self.name = name
        self.instr_list = instr_list
        self.entry_list = []
        for i in range(size):
            self.entry_list.append(RS_Entry())
        self.size = size

    def __str__(self) -> str:
        str_ = ""
        str_ += "*****"+str(self.name)+"*****\n"
        for i in range(self.size):
            str_+=self.entry_list[i].__str__()+"\n"
        return str_

    def clean(self,idx:int):
        if idx == -1:
            logging.warning("RS_cluster:{}.clean: trying to clean all the entry")
            for entry in self.entry_list:
                entry.clean()
            return
        self.entry_list[idx].clean()

    def check_empty_entry(self): #check a empty entry for new entry and return the index. If no empty ones, will return -1
        idx = -1
        for i in range(self.size):
            if not self.entry_list[i].check_occupied():
                idx = i
                break
        return idx
    
    def check_ready_entry(self): #check a ready entry to offload and return the index. If no ready ones, will return -1
        idx = -1
        for i in range(self.size):
            if self.entry_list[i].check_ready():
                idx = i
                break
        return idx

    def load(self,idx:int,instr:Instruction, target:str, operand1, operand2):
        if not (instr.type in self.instr_list):
            logging.error("RS_Cluster:{}.write(): invalid type {}".format(self.name,instr.type))
            raise Exception
        if idx >= self.size:
            logging.error("RS_Cluster:{}.write():index{} out of range".format(self.name,idx))
            raise Exception
        self.entry_list[idx].load(instr,target,operand1,operand2)

    def offload(self,idx:int,cycle):
        if idx >= self.size:
            logging.error("RS_Cluster:{}.offload():index{} out of range".format(self.name,idx))
            raise Exception
        ret_ = self.entry_list[idx].offload()
        ret_["instr"].execute = cycle
        return ret_

    def write_back(self, tag:str, value):
        for i in range(self.size):
            self.entry_list[i].write_back(tag,value)
        
    def update(self):
        for i in range(self.size):
            self.entry_list[i].update()

"""
A RS will have several entries for different instructions
 - will use a dictionary to find the entry
"""


class ReservationStations:
    def __init__(self, configs:list) -> None:
        '''format of the configs[dict,dict,...], a dict should have {"name","instr_list","size"}
        instr_list should contain all the instr names/types this cluster can accept'''
        #check format
        for config in configs:
            assert isinstance(config, dict), "ReservationStations.__init__(): configs have wrong format"
            assert "name" in config, "ReservationStations.__init__(): configs have wrong format"
            assert "instr_list" in config, "ReservationStations.__init__(): configs have wrong format"
            assert "size" in config, "ReservationStations.__init__(): configs have wrong format"
        #init RS_clusters
        self.RS_clusters = {}
        for config in configs:
            self.RS_clusters[config["name"]] = RS_Cluster(config["name"],config["instr_list"],config["size"])

    def __str__(self) -> str:
        str_ = ""
        str_ += "-----"+"ReservationStations"+"-----\n"
        for cluster_id in self.RS_clusters:
            str_ += self.RS_clusters[cluster_id].__str__() + "\n"
        return str_
        
    def clean(self, cluster_id, idx):
        '''clean the entry of given (cid,idx)
            if cid == -1, will clean all entries
            if idx == -1, will clean all entries in that cluster'''
        if cluster_id == -1:
            logging.warning("ReservationStations.clean(): trying to clean all the clusters")
            for c_id in self.RS_clusters:
                self.RS_clusters[c_id].clean(-1)
            return
        self.RS_clusters[c_id].clean(idx)
            
    def check_instr_name(self,instr):
        '''check the type of given instrution, accept Instruction or str, return cluster_id or None if not found'''
        if isinstance(instr,Instruction):
            instr_name = instr.type
        elif isinstance(instr,str):
            instr_name = instr
        else:
            logging.error("ReservationStations.check_instr_name():{} is invalid format".format(instr))
        for c_id in self.RS_clusters:
            if instr_name in self.RS_clusters[c_id].instr_list:
                return c_id
        return None
    
    def check_empty_entry(self, cluster_id):
        """ check if the cluster of given cid has empty entry
            return the entry idx if found, -1 if not found
        """
        assert cluster_id in self.RS_clusters, "ReservationStations.check_empty_entry(): invalid cluster_id "
        return self.RS_clusters[cluster_id].check_empty_entry()
    
    def check_ready_entry(self, cluster_id):
        """check a reqdy entry to offload and return the index. If no ready ones, will return -1"""
        assert cluster_id in self.RS_clusters, "ReservationStations.check_ready_entry(): invalid cluster_id "
        return self.RS_clusters[cluster_id].check_ready_entry()

    def load(self,cluster_id, idx:int,instr:Instruction, target:str, operand1, operand2):
        '''load the given informantion to the (cid,idx) entry
            input: cid, idx, instruction, target:<ROB entry name>, operand1:<ROB entry name>or <immediate number>, operand2'''
        assert cluster_id in self.RS_clusters, "ReservationStations.load(): invalid cluster_id "
        self.RS_clusters[cluster_id].load(idx,instr,target,operand1,operand2)

    def offload(self, cluster_id, idx, cycle):
        '''offload the given entry at (cid,idx)
            return value: {"type","target","value1","value2","instr"}'''
        assert cluster_id in self.RS_clusters, "ReservationStations.offload(): invalid cluster_id "
        return self.RS_clusters[cluster_id].offload(idx,cycle)
    
    def write_back(self,tag:str,value):
        """write_back using the given entry name and value
        will update all entries"""
        for c_id in self.RS_clusters:
            self.RS_clusters[c_id].write_back(tag,value)

    def update(self):
        "update all entries"
        for c_id in self.RS_clusters:
            self.RS_clusters[c_id].update()


        
    



if __name__ == "__main__":
    print("test codes")
    # # test code of RS entry
    # rse = RS_Entry()
    # print(rse)
    # rse.load(Instruction("ADD","R1","R2","R3"),"ROB1","ROB2","ROB3")
    # print(rse._type)
    # print(rse)
    # rse.write_back("ROB2",80)
    # print(rse)
    # rse.write_back("ROB2",90)
    # rse.write_back("ROB3",9)
    # print(rse)
    # rse.update()
    # print(rse)
    # print(rse.offload())
    # print(rse)
    # print( "w" in ["WWWWw","w"])
    # # test code of RS cluster
    # rsc = RS_Cluster("test",["ADD","ADDI"],5)
    # print(rsc)
    # idx = rsc.check_empty_entry()
    # rsc.load(idx,Instruction("ADD","R5","R4",3),"ROB20","ROB4","ROB10")
    # print(rsc)
    # rsc.write_back("ROB4",20)
    # rsc.update()
    # idx = rsc.check_empty_entry()
    # rsc.load(idx,Instruction("ADD","R5","R4",3),"ROB20","ROB4","ROB10")
    # print(rsc)
    # rsc.write_back("ROB10",2)
    # print(rsc)
    # idy = rsc.check_ready_entry()
    # print(idy)
    # ret = rsc.offload(idy,100)
    # print(ret)
    # print(ret["instr"])
    # print(rsc)
    # print(rsc.check_empty_entry())
    # test code of RS
    config1 = {"name":"Int","instr_list":["ADDI","SUBI"],"size":3}
    config2 = {"name":"Double","instr_list":["ADDD","SUBD"],"size":3}
    rs = ReservationStations([config1,config2])
    print(rs)

    for i in range(3):
        instr = Instruction("ADDI","R{}".format(i+2),"R{}".format(i+1),i)
        cid = rs.check_instr_name(instr)
        print(cid)
        idx = rs.check_empty_entry(cid)
        print(idx)
        rs.load(cid,idx,instr,"ROB{}".format(i+2),"ROB{}".format(i+1),i)
        # print(rs)

        instr = Instruction("SUBD","R{}".format(i+2),"R{}".format(i+1),i)
        cid = rs.check_instr_name(instr)
        print(cid)
        idx = rs.check_empty_entry(cid)
        print(idx)
        rs.load(cid,idx,instr,"ROB{}".format(i+2),"ROB{}".format(i+2),i)
        # print(rs)

    rs.update()
    print(rs)
    rs.write_back("ROB3",20)
    print(rs)

    for cid in rs.RS_clusters:
        idx = rs.check_ready_entry(cid)
        print(idx)
        if(idx != -1):
            ret = rs.offload(cid,idx,299)
            print(ret)
            print(ret["instr"])
        
    print(rs)
    

    

        
