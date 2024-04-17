import json
class Relay:
    def __init__(self,id=-1,id_group=-1,isManual=False):
        self.id = id
        self.id_group = id_group
        self.isManual = isManual

    def toJson(self):
          return {
              "id": self.id,
              "id_group": self.id_group,
              "isManual": self.isManual
          }