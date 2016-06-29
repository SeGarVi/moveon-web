from datetime import datetime, date

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

    def get_with_distance(self, station_id, userpos):
        station = self.get_by_id(station_id)
        station_pos = [station.latitude, station.longitude]
        station.distance = int(vincenty(station_pos, userpos).meters)

        return station

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
            limit_increment *= 5
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
            routes = self.get_route_info_for_station(station, n_vehicles)
            if not hasattr(station, 'routes'):
                station.routes=routes
    
    def get_route_info_for_station(self, station, n_vehicles = 1):
        routes = []
        for route, next_vehicles in self.get_station_routes(station, n_vehicles):
            route.colour = route.line.colour
            route.line_code = route.line.code
            route.line_name = route.line.name
            route.company_icon = route.line.company.logo
            route.transport = route.line.transport.name
            route.transport_type = "bus"
            route.adapted = False  #Change to the good val from de DB
            
            if len(next_vehicles) > 0:
                route.next_vehicles = [int(next_vehicle / 60) for next_vehicle in next_vehicles] 
            
            routes.append(route)
        return routes
    
    def get_route_info(self, routes):
        retroutes = []
        for route in routes:
            route.colour = route.line.colour
            route.line_code = route.line.code
            route.line_name = route.line.name
            route.company_icon = route.line.company.logo
            route.transport = route.line.transport.name
            route.transport_type = "bus"
            route.adapted = False  #Change to the good val from de DB
            
            retroutes.append(route)
        return retroutes
    
    def get_station_routes(self, station, n_vehicles):
        route_points = station.routepoint_set.all()

        routes = []
        for route_point in route_points:
            next_vehicles = []
            if route_point.time_from_beginning is not None:
                stretch = route_point.stretch

                if n_vehicles > 0:
                    next_vehicles = self._get_next_vehicles(
                                    station, route_point.time_from_beginning,
                                    stretch, n_vehicles)

            route = route_point.stretch.route
            if route not in routes:
                routes.append((route, next_vehicles))
        
        return routes


    def get_station_route_times(self, station, route_id, n_vehicles):
        route_points = station.routepoint_set.all()

        next_vehicles = []
        for route_point in route_points:
            if route_point.stretch.route.osmid == route_id:
                if route_point.time_from_beginning is not None:
                    stretch = route_point.stretch

                    if n_vehicles > 0:
                        next_vehicles = self._get_next_vehicles(
                                    station, route_point.time_from_beginning,
                                    stretch, n_vehicles)
        nvehicles=[int(next_vehicle / 60) for next_vehicle in next_vehicles]
        return nvehicles[0:n_vehicles]
    
    def _get_next_vehicles(self, station, time_from_beginning, stretch, n_vehicles):
        now = datetime.now()
        harmonized = datetime(1970,1,1, now.hour + self._get_time_zone_offset(station) , now.minute, 0, 0)
        harmonized_timestamp = int(harmonized.timestamp())
        day_of_week = now.strftime('%A').lower()
        
        timetable = stretch.time_table.filter(**{day_of_week: True}).first()
        
        next_vehicles = []
        if timetable:
            next_vehicle_times = timetable.times.filter(moment__gt=harmonized_timestamp - time_from_beginning)
            
            for next_time in next_vehicle_times[0:n_vehicles]:
                next_vehicles.append(next_time.moment + time_from_beginning - harmonized_timestamp)
        
        return next_vehicles
        
    
    def _get_time_zone_offset(self, station):
        return 1

class TimeManager(models.Manager):
    def get_by_timestamp(self, timestamp):
        return self.get(moment=timestamp)

class TimeTableManager(models.Manager):
    def get_today_valid_ids(self):
        today = date.today()
        day_of_week = today.strftime('%A').lower()
        return [tt.id for tt in self.filter(start__lte=today, end__gte=today, **{day_of_week: True})]
