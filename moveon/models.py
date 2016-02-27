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
        return str(self.osmid)
    
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
    
    objects = managers.TimeManager()
    
    class Meta:
        ordering = ['moment']
    
    def __str__(self):
        hour = int(self.moment / 1000 / 60 / 60)
        minutes = int((self.moment / 1000 / 60) % 60)
        return "%02d:%02d" % (hour, minutes)

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
    
    def __str__(self):
        return str(self.id)



class RoutePoint(models.Model):
    node = models.ForeignKey(Node)
    #stretch = models.ForeignKey(Stretch)
    order = models.IntegerField()
    distance_from_beginning = models.BigIntegerField()
    time_from_beginning = models.BigIntegerField(null=True)
    
    class Meta:
        ordering = ['order']
    
    @classmethod
    def from_osm_adapter_data(cls, osmroutepoint):
        routepoint = RoutePoint()
        
        routepoint.order = osmroutepoint['order']
        routepoint.distance_from_beginning = osmroutepoint['distance_from_beginning']
        
        return routepoint
    
    def __str__(self):
        return str(self.id)
    
class Stretch(models.Model):
    route = models.ForeignKey(Route)
    time_table = models.ManyToManyField(TimeTable)
    route_points = models.ManyToManyField(RoutePoint)
    
    def __str__(self):
        return str(self.id)