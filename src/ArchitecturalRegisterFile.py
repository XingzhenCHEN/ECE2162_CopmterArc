"""
Architectural Register File

explain the relationship between a register and a value

Exposed to programmer.


attributes
 - R_size
 - F_size
 - Key_Value  R0: 12 ...
 - Flag   check for input

methods
 - push
 - committ

"""


class ArchitecturalRegisterFile:
    def __init__(self,size0:int,size1:int):
        self.R_size = size0
        self.F_size = size1
        self.Key_Value = {}
        for i in range(self.R_size):
            self.Key_Value['R'+str(i)] = 0
        for i in range(self.F_size):
            self.Key_Value['F'+str(i)] = 0.0
        self.Key_Value['R0'] = 0
            
    def __str__(self):
        
        str_ = " "
        str_ += "\n-----Architectural Register File-----\n"
        for i in range(self.R_size):
            if (self.Key_Value['R'+str(i)] != None):
                self.Key_Value['R'+str(i)] = int(self.Key_Value['R'+str(i)])
            str_ += 'R' + str(i) + ' = ' + str(self.Key_Value['R'+str(i)]) + '\n'
        for i in range(self.F_size):
            str_ += 'F' + str(i) + ' = ' + str(self.Key_Value['F'+str(i)]) + '\n'


        return str_
    
    def push(self,register_name,value):
        length0 = len(register_name)
        length1 = len(value)
        if(length0 != length1):
            raise Exception("Error: Mismatch between name and value!")
        if(length0 > self.R_size + self.F_size):
            raise Exception("Error: Not enough ARF space!")
        
        for i in range(length0):
            self.Key_Value[register_name[i]] = value[i]
        if self.Key_Value['R0'] != 0:
            raise Exception('You can not change R0 value')

    def commit(self, register_name, value):
        if(register_name == "R0"):
            return
        self.Key_Value[register_name] = value

    def get_value(self,register_name:str):
        if register_name not in self.Key_Value:
            raise Exception("Error: The register({}) is not in ARF!".format(register_name))
        
        return self.Key_Value[register_name]
