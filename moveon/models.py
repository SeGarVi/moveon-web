from django.db import models

from osm.osm_client import OSMClient
from uuid import getnode
from django.template.defaultfilters import length

class Company(models.Model):
    name = models.TextField()
    code = models.TextField()
    url = models.URLField()
    logo = models.TextField()
    
    def __str__(self):
        return self.name
    
class Transport(models.Model):
    name = models.TextField()
    
    def __str__(self):
        return self.name

class Line(models.Model):
    company = models.ForeignKey(Company)
    transport = models.ForeignKey(Transport)
    code = models.TextField()
    name = models.TextField()
    colour = models.CharField(max_length=7)
    
    def __str__(self):
        return self.code + ' ' + self.name
    
class Route(models.Model):
    line = models.ForeignKey(Line)
    order = models.IntegerField()
    time_between_stops = models.BigIntegerField()

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

class Times(models.Model):
    time_table = models.ForeignKey(TimeTable)
    moment = models.BigIntegerField()

class Stretch(models.Model):
    route = models.ForeignKey(Route)
    sense = models.BooleanField()
    time_table = models.ManyToManyField(TimeTable)

class Place(models.Model):
    osm_id = models.BigIntegerField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    

class Station(Place):
    code = models.TextField()
    name = models.TextField(blank=True, null=True)
    adapted = models.BooleanField()
    available = models.BooleanField()
    
    def save(self, *args, **kwargs):
        if self.osm_id is not None:
            client = OSMClient()
            node = client.get_osm_node_info(str(self.osm_id))
            self.longitude = node.getLongidude()
            self.latitude = node.getLatitude()
            self.name = node.getName()
            
        super(Place, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class RoutePoint(Place):
    station = models.ForeignKey(Station)
    order = models.IntegerField()

