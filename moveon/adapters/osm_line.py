import json

class AbstractOSMLine():
    def __init__(self):
        self.line = dict()
    
    def to_json(self):
        return json.dumps(self.line)