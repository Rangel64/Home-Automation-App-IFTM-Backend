import json
class Metrics:
 
    def __init__(self,voltage = 0, current = 0, power = 0, energy = 0,frequency = 0):
        self.voltage = voltage
        self.current = current
        self.power = power
        self.energy = energy
        self.frequency = frequency
    
    def toJson(self):
        return json.dumps(self.__dict__)