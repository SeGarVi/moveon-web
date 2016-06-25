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
        logger.info('Done')
    
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
            logger.info('Getting route {0} nodes'.format(route['name']))
            
            for member in osmroute['member']:
                if self._is_station(member):
                    logger.debug('Getting station {0} info'.format(member['ref']))
                    
                    if not self._station_already_in_line(member['ref']):
                        osmstation = self._get_station_from_osm(member['ref'])
                        station = self._set_station_info(osmstation)
                        self._check_station_problems(station)
                        self.line['stations'][station['osmid']] = station
                    
                    route_point = self._get_route_point_info(
                                    member['ref'], route_point_order,
                                    distance_from_beginning, True)
                    
                    if not member['ref'] in route['route_points']:
                        route['route_points'][member['ref']] = []
                    route['route_points'][member['ref']].append(route_point)
                    
                    route_point_order += 1
                elif self._is_stop(member):
                    logger.debug('Getting stop {0} info'.format(member['ref']))
                    
                    if not self._stop_already_in_route(member['ref'], route) or \
                        self._stop_in_route_but_not_consecutive(member['ref'], previous_point):
                        if not self._stop_already_in_line(member['ref']):
                            logger.debug("\t Not present, retrieving info...")
                            
                            osmstop = self._get_stop_from_osm(member['ref'])
                            stop = self._set_stop_info(osmstop)
                            self.line['route_points'][stop['osmid']] = stop
                        
                        current_point = self.line['route_points'][member['ref']]
                        if previous_point is not None :
                            distance = \
                                self._distance_between_route_points(
                                                        previous_point, current_point)
                            distance_from_beginning += distance
                            
                        
                        route_point = self._get_route_point_info(
                                    member['ref'], route_point_order,
                                    distance_from_beginning, False)
                        
                        if not member['ref'] in route['route_points']:
                            route['route_points'][member['ref']] = []
                        route['route_points'][member['ref']].append(route_point)
                        route_point_order += 1
                        
                        previous_point = current_point
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
                        
                        if not self._node_already_in_route(node_id, route) or \
                            self._node_in_route_but_not_consecutive(node_id, previous_point):
                            if not self._node_already_in_line(node_id):
                                logger.debug("\t\t Not present, retrieving info...")
                                
                                osmnode = self._get_node_from_osm(node_id)
                                node = self._set_node_info(osmnode)
                                self.line['route_points'][node['osmid']] = node
                            
                            current_point = self.line['route_points'][node_id]
                            if previous_point is not None :
                                distance = \
                                    self._distance_between_route_points(
                                                            previous_point, current_point)
                                distance_from_beginning += distance
                            
                            route_point = self._get_route_point_info(
                                    node_id, route_point_order,
                                    distance_from_beginning, False)
                            
                            if not node_id in route['route_points']:
                                route['route_points'][node_id] = []
                            route['route_points'][node_id].append(route_point)
                            route_point_order += 1
                            
                            previous_point = current_point
    
    def _get_line_from_osm(self, line_code):
        self.osmline = self.osmapi.RelationGet(line_code)
        logger.info('Getting line {0} info'.format(self.osmline['tag']['name']))
    
    def _set_line_info(self):
        self.line['osmid'] = self.osmline['id']
        self.line['company'] = 'tib'
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
    
    def _get_route_point_info(self, node_id, route_point_order, distance, is_station):
        route_point = dict()
        route_point['node_id'] = node_id
        route_point['order'] = route_point_order
        route_point['is_station'] = is_station
        route_point['distance_from_beginning'] = distance
        return route_point
    
    def _is_stop(self, member):
        return 'stop' in member['role']
    
    def _stop_in_route_but_not_consecutive(self, stop_id, previous_point):
        return self._node_in_route_but_not_consecutive(stop_id, previous_point)
    
    def _node_in_route_but_not_consecutive(self, node_id, previous_point):
        return previous_point is not None and previous_point['osmid'] != node_id
    
    def _stop_already_in_route(self, stop_id, route):
        return self._node_already_in_route(stop_id, route)
        
    def _stop_already_in_line(self, stop_id):
        return self._node_already_in_line(stop_id)
    
    def _node_already_in_route(self, member_id, route):
        return member_id in route['route_points']
        
    def _node_already_in_line(self, member_id):
        return member_id in self.line['route_points']
    
    def _get_stop_from_osm(self, stop_id):
        return self._get_node_from_osm(stop_id)
    
    def _set_stop_info(self, osmstop):
        return self._set_node_info(osmstop)
    
    def _get_node_from_osm(self, node_id):
        return self.osmapi.NodeGet(node_id)
    
    def _set_node_info(self, osmnode):
        node = dict()
        node['osmid'] = osmnode['id']
        node['latitude'] = osmnode['lat']
        node['longitude'] = osmnode['lon']
        return node
    
    def _distance_between_route_points(self, previous_point, current_point):
        coords0 = [previous_point['latitude'], previous_point['longitude']]
        coords1 = [current_point['latitude'], current_point['longitude']]
        return int(vincenty(coords0, coords1).meters)
    
    def _is_way(self, member):
        return 'way' in member['type']
    
    def _get_way_from_osm(self, way_id):
        return self.osmapi.WayGet(way_id)