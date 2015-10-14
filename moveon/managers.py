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
        stations = self.filter(Q(longitude__gte=left) & Q(latitude__gte=bottom) &
                           Q(longitude__lte=right) & Q(latitude__lte=top))
        return stations

class NodeManager(models.Manager):
    def get_by_id(self, station_id):
        return self.get(osmid=station_id)

class RouteManager(models.Manager):
    def get_station_routes(self, station):
        node = station.node_set.all().first()
        route_points = node.routepoint_set.all()
        
        routes = []
        for route_point in route_points:
            route = route_point.stretch.route
            if route not in routes:
                routes.append(route)
        
        return routes