from django.db import models

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

class Station(models.Model):
    osmid = models.IntegerField(primary_key=True, unique=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    code = models.TextField()
    name = models.TextField()
    available = models.BooleanField()
    adapted = models.BooleanField()
    shelter = models.BooleanField()
    bench = models.BooleanField()
            
    def __str__(self):
        return self.name

class Line(models.Model):
    osmid = models.IntegerField(primary_key=True, unique=True)
    company = models.ForeignKey(Company)
    transport = models.ForeignKey(Transport)
    code = models.TextField()
    name = models.TextField()
    colour = models.CharField(max_length=7)
    stations = models.ManyToManyField(Station)
    
    def __str__(self):
        return self.code + ' ' + self.name
   
class Route(models.Model):
    osmid = models.IntegerField(primary_key=True, unique=True)
    line = models.ForeignKey(Line)
    name = models.TextField()
    station_from = models.TextField()
    station_to = models.TextField()
    
    def __str__(self):
        return self.name

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

class Node(models.Model):
    osmid = models.IntegerField(primary_key=True, unique=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    near_station = models.ForeignKey(Station, null=True)
    
    def __str__(self):
        return self.name

class Stretch(models.Model):
    route = models.ForeignKey(Route)
    time_table = models.ManyToManyField(TimeTable)

class RoutePoint():
    node = models.ForeignKey(Node)
    stretch = models.ForeignKey(Stretch)
    order = models.IntegerField()
    time_from_beggining = models.BigIntegerField()
