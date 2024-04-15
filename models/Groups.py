from typing import List
import json

class Group:
    def __init__(self,id: str, name: str, controll_pot: bool, controll_time: bool,
                 pot_max: float = 0, pot_min: float = 0,
                 time_off: str = "", time_on: str = "", relays: List[int] = []):
        self.id = id
        self.name = name
        self.controll_pot = controll_pot
        self.controll_time = controll_time
        self.pot_max = pot_max
        self.pot_min = pot_min
        self.time_off = time_off
        self.time_on = time_on
        self.relays = relays

    def toJson(self):
        return {
            'id': self.id,
            'name': self.name,
            'controll_pot': self.controll_pot,
            'controll_time': self.controll_time,
            'pot_max': self.pot_max,
            'pot_min': self.pot_min,
            'time_off': self.time_off,
            'time_on': self.time_on,
            'relays': self.relays
        }
    
