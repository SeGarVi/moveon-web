from django.db import models
from moveon import managers

class Company(models.Model):
    code = models.TextField(primary_key=True, unique=True) 
    name = models.TextField()
    url = models.URLField()
    logo = models.TextField()
    
    objects = managers.CompanyManager()
    
    def __str__(self):
        return self.name
    
class Transport(models.Model):
    name = models.TextField()
    
    objects = managers.TransportManager()
    
    def __str__(self):
        return self.name

class Node(models.Model):
    osmid = models.BigIntegerField(primary_key=True, unique=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, db_index=True)
    objects = managers.NodeManager()
    
    def __str__(self):
        return self.osmid
    
    @classmethod
    def from_osm_adapter_data(cls, osmnode):
        node = Node()
        
        node.osmid = osmnode['osmid']
        node.latitude = osmnode['latitude']
        node.longitude = osmnode['longitude']
        
        return node

class Station(Node):
    stop_node = models.ForeignKey(Node, related_name='stop_node', null=True)
    code = models.TextField()
    name = models.TextField()
    available = models.BooleanField()
    adapted = models.NullBooleanField(null=True)
    shelter = models.NullBooleanField(null=True)
    bench = models.NullBooleanField(null=True)
    
    objects = managers.StationManager()
    
    def __str__(self):
        return self.name
    
    @classmethod
    def from_osm_adapter_data(cls, osmstation):
        station = Station()
        
        station.osmid = osmstation['osmid']
        station.latitude = osmstation['latitude']
        station.longitude = osmstation['longitude']
        station.code = osmstation['code']
        station.name = osmstation['name']
        station.available = osmstation['available']
        station.adapted = osmstation['adapted']
        station.shelter = osmstation['shelter']
        station.bench = osmstation['bench']
        
        return station

class Line(models.Model):
    osmid = models.BigIntegerField(primary_key=True, unique=True)
    company = models.ForeignKey(Company)
    transport = models.ForeignKey(Transport)
    code = models.TextField()
    name = models.TextField()
    colour = models.CharField(max_length=7)
    stations = models.ManyToManyField(Station)
    
    def __str__(self):
        return self.code + ' ' + self.name
    
    @classmethod
    def from_osm_adapter_data(cls, osmline):
        line = Line()
        
        line.osmid = osmline['osmid']
        line.code = osmline['code']
        line.name = osmline['name']
        line.colour = osmline['colour']
        
        return line

class Route(models.Model):
    osmid = models.BigIntegerField(primary_key=True, unique=True)
    line = models.ForeignKey(Line)
    name = models.TextField()
    station_from = models.TextField()
    station_to = models.TextField()
    stations = models.ManyToManyField(Station)
    
    objects = managers.RouteManager()
    
    def __str__(self):
        return self.name
    
    @classmethod
    def from_osm_adapter_data(cls, osmroute):
        route = Route()
        
        route.osmid = osmroute['osmid']
        route.name = osmroute['name']
        route.station_from = osmroute['station_from']
        route.station_to = osmroute['station_to']
        
        return route

class Time(models.Model):
    moment = models.BigIntegerField(primary_key=True, unique=True)
    
    def __str__(self):
        return self.moment

class TimeTable(models.Model):
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()
    holiday = models.BooleanField()
    start = models.DateField()
    end = models.DateField()
    time_table = models.ManyToManyField(Time)

class Stretch(models.Model):
    route = models.ForeignKey(Route)
    time_table = models.ManyToManyField(TimeTable)

class RoutePoint(models.Model):
    node = models.ForeignKey(Node)
    stretch = models.ForeignKey(Stretch)
    order = models.IntegerField()
    time_from_beggining = models.BigIntegerField(null=True)
    
    @classmethod
    def from_osm_adapter_data(cls, osmroutepoint):
        routepoint = RoutePoint()
        
        routepoint.order = osmroutepoint['order']
        
        return routepoint