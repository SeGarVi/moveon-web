from datetime import datetime 

from django.db import models
from django.db.models import Q

from geopy.distance import vincenty


class CompanyManager(models.Manager):
    def get_by_code(self, company_code):
        return self.get(code=company_code)

class TransportManager(models.Manager):
    def get_by_name(self, transport_name):
        return self.get(name=transport_name)

class StationManager(models.Manager):
    def get_by_id(self, station_id):
        return self.get(osmid=station_id)

    def get_nearby_stations(self, userpos, nneareststations=5):
        max_n_stations = self.count();
        limit_increment = 0.003
        lat = userpos[0]
        lon = userpos[1]
        left   = lon - limit_increment
        right  = lon + limit_increment
        bottom = lat - limit_increment
        top    = lat + limit_increment
        
        n_stations = self.get_number_fenced_stations(bottom, left, top, right)
        while n_stations < nneareststations and n_stations < max_n_stations:
            left   = left   - limit_increment
            right  = right  + limit_increment
            bottom = bottom - limit_increment
            top    = top    + limit_increment
            n_stations = self.get_number_fenced_stations(bottom, left, top, right)
        
        stations = self.get_fenced_stations(bottom, left, top, right)
        
        for station in stations:
            station_pos = [station.latitude, station.longitude]
            station.distance = int(vincenty(station_pos, userpos).meters)
        
        ordered = sorted(stations, key=lambda x:x.distance)[:nneareststations]
        
        return ordered
    
    def get_fenced_stations(self, bottom, left, top, right):
        stations = self.filter(Q(longitude__gte=left) & Q(latitude__gte=bottom) &
                           Q(longitude__lte=right) & Q(latitude__lte=top))
        return stations
    
    def get_number_fenced_stations(self, bottom, left, top, right):
        n_stations = self.filter(Q(longitude__gte=left) & Q(latitude__gte=bottom) &
                           Q(longitude__lte=right) & Q(latitude__lte=top)).count()
        return n_stations
    
    def get_number_near_stations(self, left, bottom, right, top):
        n_stations = self.filter(Q(longitude__gte=left) & Q(latitude__gte=bottom) &
                           Q(longitude__lte=right) & Q(latitude__lte=top)).count()
        return n_stations

class NodeManager(models.Manager):
    def get_by_id(self, station_id):
        return self.get(osmid=station_id)

class RouteManager(models.Manager):
    def add_route_info_to_station_list(self, stations, n_vehicles = 1):
        for station in stations:
            self.add_route_info_to_station(station, n_vehicles)
    
    def add_route_info_to_station(self, station, n_vehicles = 1):
        if not hasattr(station, 'routes'):
            station.routes=[]
            
        for route, next_vehicles in self.get_station_routes(station, n_vehicles):
            route.colour = route.line.colour
            route.company_icon = route.line.company.logo
            route.transport = route.line.transport.name
            route.transport_type = "bus"
            route.adapted = False  #Change to the good val from de DB
            
            if len(next_vehicles) > 0:
                route.next_vehicles = [int(next_vehicle / 1000 / 60) for next_vehicle in next_vehicles] 
            
            station.routes.append(route)
    
    def get_station_routes(self, station, n_vehicles):
        route_points = station.routepoint_set.all()
        
        routes = []
        for route_point in route_points:
            stretch = route_point.stretch
            
            next_vehicles = []
            if n_vehicles > 0:
                next_vehicles = self._get_next_vehicles(station, route_point.time_from_beginning, stretch, n_vehicles)
            
            if n_vehicles == 0 or len(next_vehicles) > 0: 
                route = route_point.stretch.route
                if route not in routes:
                    routes.append((route, next_vehicles))
        
        return routes
    
    def _get_next_vehicles(self, station, time_from_beginning, stretch, n_vehicles):
        now = datetime.now()
        harmonized = datetime(1970,1,1, now.hour + self._get_time_zone_offset(station) , now.minute, 0, 0)
        harmonized_timestamp = harmonized.timestamp()*1000
        day_of_week = now.strftime('%A').lower()
        
        timetable = stretch.time_table.filter(**{day_of_week: True}).first()
        
        next_vehicles = []
        if timetable:
            next_vehicle_times = timetable.time_table.filter(moment__gt=harmonized_timestamp - time_from_beginning)
            
            for next_time in next_vehicle_times[0:n_vehicles]:
                next_vehicles.append(next_time.moment + time_from_beginning - harmonized_timestamp)
        
        return next_vehicles
        
    
    def _get_time_zone_offset(self, station):
        return 2

class TimeManager(models.Manager):
    def get_by_timestamp(self, timestamp):
        return self.get(moment=timestamp)
