class OsmWay():
    def __init__(self, osm_id, name, bench, shelter,
                 wheelchair, tram, bus, train):
        self.osm_id = osm_id
        self.name = name
        self.bench = bench
        self.shelter = shelter
        self.wheelchair = wheelchair
        self.tram = tram
        self.bus = bus
        self.train = train
    
    def __str__(self):
        output = u"""OpenStreetMap node:\n
                     \tId: {0}\n
                     \tName: {1}\n
                     \tShelter: {2}\n
                     \tBench: {2}\n
                     \tWheelchair: {2}\n
                     \tTram: {2}\n
                     \tTrain: {2}\n
                     \tBus: {2}\n"""
        return output.format(self.osm_id, self.name, self.shelter, self.bench,
                             self.wheelchair, self.tram, self.train, self.bus)