from rest_framework import serializers
from asyncio.transports import Transport

class RouteSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    #line = serializers.ForeignKey(Line)
    name = serializers.CharField()
    station_from = serializers.CharField()
    station_to = serializers.CharField()
    colour = serializers.CharField(required=False)
    company_icon = serializers.URLField(required=False)
    transport = serializers.CharField(required=False)
    adapted = serializers.BooleanField(required=False)
    next_vehicles = serializers.ListField(required=False)
    #stations = serializers.ManyToManyField(Station)

class StationSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    code = serializers.CharField()
    name = serializers.CharField()
    available = serializers.BooleanField()
    adapted = serializers.BooleanField()
    shelter = serializers.BooleanField()
    bench = serializers.BooleanField()
    distance= serializers.IntegerField(required=False)
    routes = RouteSerializer(many=True, read_only=True)

class LineSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    #company = models.ForeignKey(Company)
    #transport = models.ForeignKey(Transport)
    code = serializers.CharField()
    name = serializers.CharField()
    colour = serializers.CharField(max_length=7)
    #stations = models.ManyToManyField(Station)

class CompanySerializer(serializers.Serializer):
    pk = serializers.CharField(read_only=True) 
    name = serializers.CharField()
    url = serializers.URLField()
    logo = serializers.CharField()