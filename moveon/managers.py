from django.db import models
from moveon.models import Line, Station, Node

class OSMLineManager(models.Manager):
    def __init__(self, osmline):
        self.osmline = osmline
        self.stations = dict()
        self.routes = []
        self.nodes = dict()
        self.stretches = dict()
    
    def save(self):
        self._save_line()
        self._save_stations()
        self._assign_stations_to_line()
        self._save_nodes()
        self._save_routes()
        self._create_default_stretches()
        self._save_route_points()
    
    def _save_line(self)
        companymanager = CompanyManager()
        company = companymanager.get_by_id(self.osmline['company'])
        
        transportmanager = TransportManager()
        transport = transportmanager.get_by_id(self.osmline['transport'])
        
        self.line = Line.from_osm_adapter_data(self.osmlines)
        self.line.company = company
        self.line.transport = transport
        
        self.line.save()
    
    def _save_stations(self):
        stationmanager = StationManager()
        
        for osmstation in self.osmline['stations']:
            station = stationmanager.get_by_id(osmstation['osmid'])
            
            if not station:
                station = Station.from_osm_adapter_data(osmstation)
                station.save()
            
            self.stations[station.osmid] = station
    
    def _assign_stations_to_line(self):
        self.line.stations = self.stations.values()
        self.line.save()
    
    def _save_nodes(self)
        nodemanager = NodeManager()
        
        for osmnode in self.osmline['route_points']:
            node = nodemanager.get_by_id(osmnode['osmid'])
            
            if not node:
                node = Node.from_osm_adapter_data(osmnode)
                
                if 'near_station' in osmnode:
                    node.near_station = self.stations[osmnode['near_station']]
            
                node.save()
                self.nodes[node.osmid] = node
    
    def _save_routes(self):
        for osmroute in self.osmline['routes']:
            route = Route.from_osm_adapter_data(osmroute)
            route.line = self.line
            route.save()
            self.routes.append(route)
    
    def _create_default_stretches(self):
        for route in self.routes
            stretch = Stretch()
            stretch.route = route
            stretch.save()
            self.stretches[route.osmid] = stretch
    
    def _save_route_points(self):
        for osmroute in self.osmline['routes']:
            for osmroutepoint in osmroute['route_points']
                routepoint = RoutePoint.from_osm_adapter_data(osmroutepoint)
                routepoint.node = self.nodes[osmroutepoint['node_id']]
                routepoint.node = self.stretches[osmroute['osmid']]
                routepoint.save()
    
class CompanyManager(models.Manager):
    def get_by_id(self, company_id):
        return self.get(id = company_id)

class TransportManager(models.Manager):
    def get_by_id(self, transport_id):
        return self.get(id = transport_id)

class StationManager(models.Manager):
    def get_by_id(self, station_id):
        return self.get(id = station_id)

class LineManager(models.Manager):
   
class RouteManager(models.Manager):

class TimeManager(models.Manager):

class TimeTableManager(models.Manager):

class NodeManager(models.Manager):
    def get_by_id(self, station_id):
        return self.get(id = station_id)

class StretchManager(models.Manager):

class RoutePointManager(models.Manager):
