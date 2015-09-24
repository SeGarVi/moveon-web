from django.db import models
from django.db.models import Q

class CompanyManager(models.Manager):
    def get_by_code(self, company_code):
        return self.get(code=company_code)

class TransportManager(models.Manager):
    def get_by_name(self, transport_name):
        return self.get(name=transport_name)

class StationManager(models.Manager):
    def get_by_id(self, station_id):
        return self.get(osmid=station_id)
    
    def get_near_stations(self, left, bottom, right, top):
        stations = self.filter(Q(latitude__gte=left) & Q(longitude__gte=bottom) &
                           Q(latitude__lte=right) & Q(longitude__lte=top))
        return stations

class NodeManager(models.Manager):
    def get_by_id(self, station_id):
        return self.get(osmid=station_id)
