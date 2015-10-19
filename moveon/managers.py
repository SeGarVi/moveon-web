from datetime import datetime 

from django.db import models
from django.db.models import Q
from django.db.models import F

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
        stations = self.filter(Q(longitude__gte=left) & Q(latitude__gte=bottom) &
                           Q(longitude__lte=right) & Q(latitude__lte=top))
        return stations
    
    def get_number_near_stations(self, left, bottom, right, top):
        n_stations = self.filter(Q(longitude__gte=left) & Q(latitude__gte=bottom) &
                           Q(longitude__lte=right) & Q(latitude__lte=top)).count()
        return n_stations

class NodeManager(models.Manager):
    def get_by_id(self, station_id):
        return self.get(osmid=station_id)

class RouteManager(models.Manager):
    def get_station_routes(self, station, n_vehicles):
        route_points = station.routepoint_set.all()
        
        routes = []
        for route_point in route_points:
            stretch = route_point.stretch
            
            next_vehicles = []
            if n_vehicles > 0:
                next_vehicles = self._get_next_vehicles(station, route_point.time_from_beggining, stretch, n_vehicles)
            
            if n_vehicles == 0 or len(next_vehicles) > 0: 
                route = route_point.stretch.route
                if route not in routes:
                    routes.append((route, next_vehicles))
        
        return routes
    
    def _get_next_vehicles(self, station, time_from_beggining, stretch, n_vehicles):
        now = datetime.now()
        harmonized = datetime(1970,1,1, now.hour + self._get_time_zone_offset(station) , now.minute, 0, 0)
        harmonized_timestamp = harmonized.timestamp()*1000
        day_of_week = now.strftime('%A').lower()
        
        timetable = stretch.time_table.filter(**{day_of_week: True}).first()
        
        next_vehicles = []
        if timetable:
            next_vehicle_times = timetable.time_table.filter(moment__gt=harmonized_timestamp - time_from_beggining)
            
            for next_time in next_vehicle_times[0:n_vehicles]:
                next_vehicles.append(next_time.moment + time_from_beggining - harmonized_timestamp)
        
        return next_vehicles
        
    
    def _get_time_zone_offset(self, station):
        return 2

class TimeManager(models.Manager):
    def get_by_timestamp(self, timestamp):
        return self.get(moment=timestamp)