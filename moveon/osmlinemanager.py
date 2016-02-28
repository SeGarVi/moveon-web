import logging

from moveon.models import Company, Transport, Line, Station, Node, Route, Stretch, RoutePoint

logger = logging.getLogger(__name__)

class OSMLineManager():
    def __init__(self, osmline):
        self.osmline = osmline
        self.stations = dict()
        self.routes = []
        self.nodes = dict()
        self.stretches = dict()
    
    def save(self):
        self._save_line()
        self._save_nodes()
        self._save_stations()
        self._assign_stations_to_line()
        self._save_routes()
        self._create_default_stretches()
        self._save_route_points()
    
    def _save_line(self):
        logger.debug('Saving line')
        company = Company.objects.get_by_code(self.osmline['company'])
        transport = Transport.objects.get_by_name(self.osmline['transport'])
        
        self.line = Line.from_osm_adapter_data(self.osmline)
        self.line.company = company
        self.line.transport = transport
        
        self.line.save()
    
    def _save_nodes(self):
        logger.debug('Saving nodes')
        for osmnode in self.osmline['route_points'].values():
            try:
                node = Node.objects.get_by_id(osmnode['osmid'])
            except Node.DoesNotExist:
                node = Node.from_osm_adapter_data(osmnode)
                node.save()
                
            self.nodes[node.osmid] = node
    
    def _save_stations(self):
        logger.debug('Saving stations')
        for osmstation in self.osmline['stations'].values():
            try:
                station = Station.objects.get_by_id(osmstation['osmid'])
            except Station.DoesNotExist:
                station = Station.from_osm_adapter_data(osmstation)
                station.stop_node = self.nodes[osmstation['stop_node']]
                station.save()
            
            self.stations[station.osmid] = station
            self.nodes[station.osmid] = station
    
    def _assign_stations_to_line(self):
        logger.debug('Assigning stations to line')
        self.line.stations = self.stations.values()
        self.line.save()
    
    def _save_routes(self):
        logger.debug('Saving routes')
        for osmroute in self.osmline['routes'].values():
            route = Route.from_osm_adapter_data(osmroute)
            route.line = self.line
            route.save()
            self.routes.append(route)
    
    def _create_default_stretches(self):
        logger.debug('Creating default stretches')
        for route in self.routes:
            stretch = Stretch()
            stretch.route = route
            stretch.save()
            self.stretches[route.osmid] = stretch
    
    def _save_route_points(self):
        logger.debug('Saving route points')
        for osmroute in self.osmline['routes'].values():
            for osmroutepoint in osmroute['route_points'].values():
                routepoint = RoutePoint.from_osm_adapter_data(osmroutepoint)
                routepoint.node = self.nodes[osmroutepoint['node_id']]
                routepoint.stretch = self.stretches[osmroute['osmid']]
                routepoint.save()
