"""
The init stage will be mainly implemented in the main.py, here we only imeplement somre help functions

The task of init stage
 - load the configs
 - load the registers
 - load the instrs
 - load the data
 - instantiate all needed classes 
"""

"""
load configs
 - here we utilize a 2-step load manner to load all the configs
 - 1. we use a Config() class to store a set of default configs, and also help reformat the configs when instatiate the classes
 - 2.(1) we implement a parse() method, which accepts a .txt whose format is the same as which in the project description, which is obviously a subset of the configs
 - 2.(2) we can also modify the config object to self-define the configs
"""
import os
import copy
from ProcessingUnits import PU_config
from Instruction import Instruction
class Config:
    """The __<..> will be changed by other attrs, please don't modify them, modify other public attrs instead"""
    #MeM, Queue, ARF,RAT & ROB
    __instrMemConfig = {}
    instrQueueSize = 10
    __instrQueueConfig = {"size":instrQueueSize}
    numRReg = 32
    numFReg = 32
    __ARFConfig = {"size1":numRReg,"size2":numFReg}
    __RATConfig = {"size1":numRReg,"size2":numFReg}
    ROB_size = 64
    __ROBConfig = {"size":64}

    #RS
    clusterNames = ["Integer adder","FP adder","FP multiplier"]
    instrLists = [
        ["Add","Addi","Sub","NOP","Beq","Bne"],
        ["Add.d","Sub.d"],
        ["Mult.d"]
    ]
    RSSizes = [4,3,2]
    __RSConfig = []
    #PU Config
    latency_configs = {
        "Add":1,"Addi":1,"Sub":1,"NOP":1,"Bne":1,"Beq":1,
        "Add.d":4,"Sub.d":4,
        "Mult.d":15
    }
    compute_configs = {
        "Add":PU_config.add,"Addi":PU_config.add,"Sub":PU_config.sub,"NOP":PU_config.nop,
        "Add.d":PU_config.add,"Sub.d":PU_config.sub,
        "Mult.d":PU_config.multiply,
        "Beq":PU_config.equal,"Bne":PU_config.nequal
    }
    PUEntries = [1,1,1]
    PUBufferSizes = [1,1,1]
    __PUConfig = []
    #Memory configs
    memRSEntries = 3
    memPUEntries = 1
    memExecLatency = 1
    memMemLatency = 4
    #runtime configs
    #Currently not used
    # fetch_config = {}
    # issue_config = {}
    # execute_config = {}
    # memory_conifg = {}
    # writeBack_config = {}
    # commit_config = {}

    #Reg and memory info
    regInfo = {}
    dataMemInfo= {}
    instrMemInfo = []

    #####
    #methods

    def getInstrMemConfig(self):
        "not used since instantiate instrMem doesn't need a param"
        return None
    def getInstrQueueConfig(self):
        """return {'size'}"""
        return self.__instrQueueConfig
    def getARFConfig(self):
        """return {'size1','size2'}"""
        self.__ARFConfig["size1"] = self.numRReg
        self.__ARFConfig["size2"] = self.numFReg
        return self.__ARFConfig
    def getRATConfig(self):
        """return{'size1,'size2'}"""
        self.__RATConfig["size1"] = self.numRReg
        self.__RATConfig["size2"] = self.numFReg
        return self.__RATConfig
    def getROBConfig(self):
        """return{'size'}"""
        self.__ROBConfig["size"] = self.ROB_size
        return self.__ROBConfig
    def getRSConfig(self):
        """return [{"name","instr_list","size"}...]"""
        #check the attributes
        assert len(self.clusterNames) == len(self.instrLists)
        assert len(self.clusterNames) == len(self.RSSizes)
        #group the configs
        for i in range(len(self.clusterNames)):
            self.__RSConfig.append({"name":self.clusterNames[i],"instr_list":self.instrLists[i],"size":self.RSSizes[i]})
        return self.__RSConfig
    def getOutputConfig(self):
        """return {
        "Add":1,"Addi":1,"Sub":1,"NOP":1,
        "Add.d":4,"Sub.d":4,
        "Mult.d":15,"memExecLatency":1,"memMemLatency":4
        }"""
        output_configs = copy.deepcopy(self.latency_configs)
        output_configs['memExecLatency'] = self.memExecLatency
        output_configs['memMemLatency'] = self.memMemLatency
        return output_configs
    def __getPU_Config(self):
        """return a PU_config"""
        config = PU_config(self.latency_configs,self.compute_configs)
        return config
    def getPUConfig(self):
        """return[{'name','instr_list','size','buffer_size','config':PU_config}...]"""
        assert len(self.clusterNames) == len(self.instrLists)
        assert len(self.clusterNames) == len(self.PUEntries)
        assert len(self.clusterNames) == len(self.PUBufferSizes)
        config = self.__getPU_Config()
        for i in range(len(self.clusterNames)):
            self.__PUConfig.append({'name':self.clusterNames[i],
                                    'instr_list':self.instrLists[i],
                                    'size':self.PUEntries[i],
                                    'buffer_size':self.PUBufferSizes[i],
                                    'config':config
                                    })
        return self.__PUConfig
    def __str__(self):
        str_ = ""
        str_ += "-----Configs-----\n"
        str_ += "*****Entries*****\n"
        str_ += "InstrQueue: {}\n".format(self.instrQueueSize)
        str_ += "Registers:(ARF & RAT) Int: {}, Float: {}\n".format(self.numRReg,self.numFReg)
        str_ += "ROB: {}\n".format(self.ROB_size)
        str_ += "RS & PU entries:\n"
        str_ += "- clusters:\t"
        for item in self.clusterNames:
            str_ += str(item) + "\t"
        str_ += "\n- RS Entries:\t"
        for item in self.RSSizes:
            str_ += str(item) + "\t"
        str_ += "\n- PU Entries:\t"
        for item in self.PUEntries:
            str_ += str(item) + "\t"
        str_ += "\n- CDB buffer\t"
        for item in self.PUBufferSizes:
            str_ += str(item) + "\t"
        str_ += "\n*****ISA configs*****\n"
        str_ += "Instruction handler:\n"
        for i in range(len(self.clusterNames)):
            str_ += self.clusterNames[i] + ":\t"
            for instr in self.instrLists[i]:
                str_ += str(instr)+"({})".format(self.latency_configs[str(instr)]) +"\t"
            str_ += "\n"
        str_ += "*****Memory configs*****\n"
        str_ += "RS entries:{},\tPU entries:{},\tExec latency:{},\tMem latency:{}\n".format(
            self.memRSEntries,self.memPUEntries,self.memExecLatency,self.memMemLatency
        )
        str_ += "*****Registers*****\n"
        str_ += self.regInfo.__str__() + "\n"
        str_ += "*****Data Memory*****\n"
        str_ += self.dataMemInfo.__str__() + "\n"
        str_ += "*****Instr Memory*****\n"
        for instr in self.instrMemInfo:
            str_ += instr.__str__().replace("None", "").replace("|","")+ "\n"
        return str_
    def __parse_ISA(self,config_list:list):
        # print(config_list)
        for i in range(len(config_list)-1):#here we only parse the PU settings
            config_line = config_list[i]
            assert isinstance(config_line,str)
            config_line = config_line.replace("\n","")
            split_line = config_line.split('\t')
            #get cluster name
            self.clusterNames[i] = split_line[0]
            self.RSSizes[i] = int(split_line[1])
            #get latency
            for instr in self.instrLists[i]:
                self.latency_configs[instr] = int(split_line[2])
            self.PUEntries[i] = int(split_line[4])
        
        #parse memory settings
        config_line = config_list[-1]
        assert isinstance(config_line,str)
        config_line = config_line.replace("\n","")
        split_line = config_line.split('\t')
        self.memRSEntries = int(split_line[1])
        self.memExecLatency = int(split_line[2])
        self.memMemLatency = int(split_line[3])
        self.memPUEntries = int(split_line[4])
    def __parse_entries(self,config_list:list):
        #parse ROB entry settings
        config_line = config_list[0]
        assert isinstance(config_line,str)
        config_line = config_line.replace("\n","")
        split_line = config_line.split('=')
        self.ROB_size = int(split_line[-1])

        #parse CDB buffer size
        config_line = config_list[1]
        assert isinstance(config_line,str)
        config_line = config_line.replace("\n","")
        split_line = config_line.split('=')
        for i in range(len(self.PUBufferSizes)):
            self.PUBufferSizes[i] = int(split_line[-1])
        
    def __parse_regs(self,config:str):
        config = config.replace("\n","").replace(" ","")
        reg_list = config.split(",")
        for i in range(len(reg_list)):
            reg_list[i] = reg_list[i].split("=")
        # print(reg_list)
        for reg in reg_list:
            self.regInfo[reg[0].replace(" ","")] = float(reg[1])
        # print(reg_list)
        # print(self.regInfo)
    def __parse_mem(self,config:str):
        # print(config)
        config = config.replace("\n","")
        memory_dict = {}

        # 分割字符串并去除空格
        entries = config.split(',')
        entries = [entry.strip() for entry in entries]
    
        # 处理每个条目
        for entry in entries:
            # 提取键和值
            key_val = entry.split('=')
            key, val = key_val[0].strip(), key_val[1].strip()
        
            # 提取内存地址和值
            start_idx = key.find('[') + 1
            end_idx = key.find(']')
            address = int(key[start_idx:end_idx])

            # 存储到字典中
            memory_dict[address] = float(val)

        self.dataMemInfo = memory_dict

        # mem_list = config.split(",")
        # for i in range(len(mem_list)):
        #     mem_list[i] = mem_list[i].split("=")
        #     mem_list[i][0] = mem_list[i][0].replace("Mem[","")
        #     mem_list[i][0] = mem_list[i][0].replace("]","")
        #     mem_list[i][0] = int(mem_list[i][0])
        #     mem_list[i][1] = float(mem_list[i][1])
        #     self.dataMemInfo[mem_list[i][0]] = mem_list[i][1]


    def __parse_instr(self,config_list):
        '''the mem instr will be parsed as Ld/Sd, operand1, offset(reg), None'''
        # parse usual instr
        for i in range(len(config_list)):
            config_list[i] = config_list[i].replace("\n","")
            if "NOP" in config_list[i]:
                config_list[i] = "NOP R0, 0, 0"
            config_list[i] = config_list[i].split(",")
            for j in range(len(config_list[i])):
                if (not 'R' in config_list[i][j]) and (not 'F' in config_list[i][j]) and (not 'NOP' in config_list[i][j]):
                    config_list[i][j] = float(config_list[i][j])
            #parse the first element
            config_list[i][0] = config_list[i][0].split(' ')

            #form instr
            target = config_list[i][0][0]
            if isinstance(target, str): target.replace(" ","")
            operand1 = config_list[i][0][1]
            if isinstance(operand1, str): operand1.replace(" ","")
            operand2 = config_list[i][1]
            if isinstance(operand2, str): operand2.replace(" ","")
            operand3 = None
            if(len(config_list[i])==3):
                operand3 = config_list[i][2]
                if isinstance(operand3, str): operand3.replace(" ","")

            instr = Instruction(target,operand1,operand2,operand3)
            self.instrMemInfo.append(instr)
        # print(self.instrMemInfo)
        
    def parse(self,path:str):
        """file config limitations:
        1. the ISA part:
            - should end with a empty line
        2. the ROB and CDB entries
            - strictly takes one line each
        3. Regs and Memories
            - strictly takes one line each
            - there should be a empty line after the Memories configs
        4. Instrs 
            - take multiple lines
        """
        config_file = open(path)
        config_list = config_file.readlines()
        self.__parse_ISA(config_list[1:5])
        self.__parse_entries(config_list[6:8])
        self.__parse_regs(config_list[8])
        self.__parse_mem(config_list[9])
        self.__parse_instr(config_list[11:])

        


if __name__ == '__main__':
    config = Config()
    print(config)
    config.parse(os.path.realpath("inputs")+"/input1.txt")
    print(config)


