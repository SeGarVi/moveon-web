import logging

from osmapi import OsmApi
from osmlineadapters.osm_line import AbstractOSMLine
from geopy.distance import vincenty

logger = logging.getLogger(__name__)

class OSMLine(AbstractOSMLine):
    def __init__(self, line_id):
        super(OSMLine, self).__init__()
        
        self.osmapi = OsmApi()
        self._get_line(line_id)
        self._get_routes()
        self._get_route_points()
    
    def _get_line(self, line_id):
        self._get_line_from_osm(line_id)
        self._set_line_info()
    
    def _get_routes(self):
        logger.info('Getting route info')
        self.osmroutes = []
        for member in self.osmline['member']:
            if self._is_route(member):
                osmroute = self._get_route_from_osm(member['ref'])
                self._set_route_info(osmroute)
    
    def _get_route_points(self):
        ways = dict()
        logger.debug('Getting route point info')
        for osmroute in self.osmroutes:
            route = self.line['routes'][osmroute['id']]
            route_point_order = 1
            distance_from_beginning = 0
            previous_point = None
            #previous_route_point = None
            logger.info('Getting route {0} nodes'.format(route['name']))
            
            for member in osmroute['member']:
                if self._is_station(member):
                    logger.debug('Getting station {0} info'.format(member['ref']))
                    
                    if not self._station_already_in_line(member['ref']):
                        osmstation = self._get_station_from_osm(member['ref'])
                        station = self._set_station_info(osmstation)
                        self._check_station_problems(station)
                        self.line['stations'][station['osmid']] = station
                    
                    #distance = previous_route_point['distance_from_beginning']
                    route_point = self._get_route_point_info(
                                    self, member, route_point_order,
                                    distance_from_beginning)
                    route['route_points'][member['ref']] = route_point
                    route_point_order += 1
                elif self._is_stop(member):
                    logger.debug('Getting stop {0} info'.format(member['ref']))
                    
                    if not self._stop_already_in_route(member, route) and \
                       not self._stop_already_in_line(member):
                        logger.debug("\t Not present, retrieving info...")
                        
                        osmstop = self._get_stop_from_osm(member['ref'])
                        stop = self._set_stop_info(osmstop)
                        self.line['route_points'][stop['osmid']] = stop
                        
                        if previous_point is not None :
                            distance = \
                                self._distance_between_route_points(
                                                        previous_point, stop)
                            distance_from_beginning += distance
                            
                        
                        route_point = self._get_route_point_info(
                                    self, member, route_point_order,
                                    distance_from_beginning)
                        route['route_points'][member['ref']] = route_point
                        route_point_order += 1
                        
                        previous_point = stop
                        #previous_route_point = route_point
                elif self._is_way(member):
                    logger.debug('Getting way {0} info'.format(member['ref']))
                    if member['ref'] not in ways:
                        logger.debug("\t Not present, retrieving info...")
                        way = self._get_way_from_osm(member['ref'])
                        ways[member['ref']] = way
                    else:
                        way = ways[member['ref']]
                    
                    for node_id in way['nd']:
                        logger.debug('\tGetting node {0} info'.format(node_id))
                        
                        if node_id not in route['route_points']:
                            if node_id not in self.line['route_points']:
                                logger.debug("\t\t Not present, retrieving info...")
                                
                                osmnode = self.osmapi.NodeGet(node_id)
                                node = dict()
                                node['osmid'] = osmnode['id']
                                node['latitude'] = osmnode['lat']
                                node['longitude'] = osmnode['lon']
                                
                                self.line['route_points'][node['osmid']] = node
                            
                            current_point = self.line['route_points'][node_id]
                            if previous_point is not None :
                                previous_coords = [previous_point['latitude'], previous_point['longitude']]
                                current_coords = [current_point['latitude'], current_point['longitude']]
                                distance = int(vincenty(previous_coords, current_coords).meters)
                                distance_from_beginning += distance
                            
                            route_point = dict()
                            route_point['node_id'] = node_id
                            route_point['order'] = route_point_order
                            route_point['distance_from_beginning'] = distance_from_beginning
                            route['route_points'][node_id] = route_point
                            route_point_order += 1
                            
                            previous_point = current_point
                            #previous_route_point = route_point
    
    def _get_line_from_osm(self, line_code):
        logger.info('Getting line {0} info'.format(self.osmline['tag']['name']))
        self.osmline = self.osmapi.RelationGet(line_code)
    
    def _set_line_info(self):
        self.line['osmid'] = self.osmline['id']
        self.line['company'] = 'emt_palma'
        self.line['transport'] = 'bus'
        self.line['code'] = str(self.osmline['tag']['ref'])
        self.line['name'] = self.osmline['tag']['name']
        self.line['colour'] = self.osmline['tag']['colour']
        self.line['stations'] = dict()
        self.line['route_points'] = dict()
        self.line['routes'] = dict()
        self.line['problems'] = []
    
    def _is_route(self, member):
        return 'relation' in member['type']
    
    def _get_route_from_osm(self, route_id):
        osmroute = self.osmapi.RelationGet(route_id)
        self.osmroutes.append(osmroute)
        return osmroute
    
    def _set_route_info(self, osmroute):
        route = dict()
        route['osmid'] = osmroute['id']
        route['name'] = osmroute['tag']['name']
        route['station_from'] = osmroute['tag']['from'] 
        route['station_to'] = osmroute['tag']['to']
        route['route_points'] = dict()
        self.line['routes'][route['osmid']] = route
    
    def _is_station(self, member):
        return 'platform' in member['role']
    
    def _station_already_in_line(self, station):
        return station in self.line['stations']
    
    def _get_station_from_osm(self, station_id):
        return self.osmapi.NodeGet(station_id)
    
    def _set_station_info(self, osmstation):
        station = self._get_station_basic_info(osmstation)
        self._set_station_related_stop(osmstation, station)
        return station
    
    def _get_station_basic_info(self, osmstation):
        station = dict()
        station['osmid'] = osmstation['id'] 
        station['latitude'] = osmstation['lat']
        station['longitude'] = osmstation['lon']
        station['code'] = str(osmstation['tag']['ref'])
        station['name'] = osmstation['tag']['name']
        station['available'] = True
        
        if 'wheelchair' in osmstation['tag']:
            station['adapted'] = 'yes' in osmstation['tag']['wheelchair']
        else:
            station['adapted'] = None
        
        if 'shelter' in osmstation['tag']:
            station['shelter'] = 'yes' in osmstation['tag']['shelter']
        else:
            station['shelter'] = None
        
        if 'bench' in osmstation['tag']:
            station['bench'] = 'yes' in osmstation['tag']['bench']
        else:
            station['bench'] = None
        
        return station
    
    def _set_station_related_stop(self, osmstation, station):
        station_relations = self._get_station_relations_from_osm(osmstation)
        for relation in station_relations:
            if self._is_public_transport_relation(relation):
                if self._is_stop_area(relation):
                    stop_area_members = relation['member']
                    for stop_area_member in stop_area_members:
                        if self._is_stop_area_stop(stop_area_member):
                            station['stop_node'] = stop_area_member['ref']
                    break
    
    def _get_station_relations_from_osm(self, osmstation):
        return self.osmapi.NodeRelations(osmstation['id'])
    
    def _is_public_transport_relation(self, relation):
        return 'public_transport' in relation['tag']
    
    def _is_stop_area(self, relation):
        return 'stop_area' in relation['tag']['public_transport']
    
    def _is_stop_area_stop(self, stop_area_member):
        return 'stop' in stop_area_member['role']
    
    def _check_station_problems(self, station):
        if self._station_has_no_related_stop(station):
            problem = ['Stop area problem', station['osmid'], station['name']]
            self.line['problems'].append(problem)
    
    def _station_has_no_related_stop(self, station):
        return 'stop_node' not in station
    
    def _get_route_point_info(self, member, route_point_order, distance):
        route_point = dict()
        route_point['node_id'] = member['ref']
        route_point['order'] = route_point_order
        route_point['distance_from_beginning'] = distance
        return route_point
    
    def _is_stop(self, member):
        return 'stop' in member['role']
    
    def _stop_already_in_route(self, member, route):
        return member['ref'] in route['route_points']
        
    def _stop_already_in_line(self, member):
        return member['ref'] not in self.line['route_points']
    
    def _get_stop_from_osm(self, stop_id):
        return self.osmapi.NodeGet(stop_id)
    
    def _set_stop_info(self, osmstop):
        stop = dict()
        stop['osmid'] = osmstop['id']
        stop['latitude'] = osmstop['lat']
        stop['longitude'] = osmstop['lon']
        return stop
    
    def _distance_between_route_points(self, previous_point, current_point):
        coords0 = [previous_point['latitude'], previous_point['longitude']]
        coords1 = [current_point['latitude'], current_point['longitude']]
        return int(vincenty(coords0, coords1).meters)
    
    def _is_way(self, member):
        return 'way' in member['type']
    
    def _get_way_from_osm(self, way_id):
        return self.osmapi.WayGet(way_id)