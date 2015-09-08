class OsmNode:
    def __init__(self, id, latitude, longitude, name,
                 shelter=True, bench=False, wheelchair=False):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.name = name
        self.shelter = shelter
        self.bench = bench
        self.wheelchair = wheelchair
    
    def getId(self):
        return self.id
    
    def getName(self):
        return self.name;
    
    def getLatitude(self):
        return self.latitude
    
    def getLongidude(self):
        return self.longitude
    
    def __str__(self):
        output = u"""OpenStreetMap node:\n
                     \tId: {0}\n
                     \tName: {1}\n
                     \tLatitude: {2}\n
                     \tLongitude: {3}\n
                     \tShelter: {2}\n
                     \tBench: {2}\n
                     \tWheelchair: {2}\n"""
        return output.format(self.id, self.name, self.latitude, self.longitude,
                             self.shelter, self.bench, self.wheelchair)