class OsmNode:
    def __init__(self, osm_id, latitude, longitude, name):
        self.id = osm_id
        self.latitude = latitude
        self.longitude = longitude
        self.name = name;
    
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
                     \tLongitude: {3}\n"""
        return output.format(self.id, self.name, self.latitude, self.longitude)