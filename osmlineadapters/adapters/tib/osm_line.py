import logging

from osmapi import OsmApi
from osmlineadapters.osm_line import AbstractOSMLine
from geopy.distance import vincenty

logger = logging.getLogger(__name__)

class OSMLine(AbstractOSMLine):
    def __init__(self, line_code):
        super(OSMLine, self).__init__()
        
        self.osmapi = OsmApi()
        self._get_line_from_osm(line_code)
        self._get_line_routes()
        self._get_line_route_points()
    
    def _get_line_from_osm(self, line_code):
        self.osmline = self.osmapi.RelationGet(line_code)
        logger.info('Getting line {0} info'.format(self.osmline['tag']['name']))
        
        self.line['osmid'] = self.osmline['id']
        self.line['company'] = 'emt_palma'
        self.line['transport'] = 'bus'
        self.line['code'] = str(self.osmline['tag']['ref'])
        self.line['name'] = self.osmline['tag']['name']
        self.line['colour'] = self.osmline['tag']['colour']
        self.line['stations'] = dict()
        self.line['route_points'] = dict()
        self.line['routes'] = dict()
    
    def _get_line_routes(self):
        logger.info('Getting route info')
        self.osmroutes = []
        for member in self.osmline['member']:
            if 'relation' in member['type']:
                osmroute = self.osmapi.RelationGet(member['ref'])
                self.osmroutes.append(osmroute)
                
                logger.info('Getting route {0} info'.format(osmroute['tag']['name']))
                
                route = dict()
                route['osmid'] = osmroute['id']
                route['name'] = osmroute['tag']['name']
                route['station_from'] = osmroute['tag']['from'] 
                route['station_to'] = osmroute['tag']['to']
                route['route_points'] = dict()
                self.line['routes'][route['osmid']] = route
    
    def _get_line_route_points(self):
        ways = dict()
        logger.debug('Getting route point info')
        for osmroute in self.osmroutes:
            route = self.line['routes'][osmroute['id']]
            route_point_order = 1
            distance_from_beginning = 0
            previous_point = None
            previous_route_point = None
            logger.info('Getting route {0} nodes'.format(route['name']))
            
            for member in osmroute['member']:
                if 'platform' in member['role']:
                    logger.debug('Getting station {0} info'.format(member['ref']))
                    
                    if member['ref'] not in self.line['stations']:
                        osmstation = self.osmapi.NodeGet(member['ref'])
                        
                        logger.debug("\t Not present, retrieving info of {0}...".format(osmstation['tag']['name']))
                        
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
                        
                        node_relations = self.osmapi.NodeRelations(osmstation['id'])
                        for relation in node_relations:
                            if 'public_transport' in relation['tag']:
                                if 'stop_area' in relation['tag']['public_transport']:
                                    for sa_member in relation['member']:
                                        if 'stop' in sa_member['role']:
                                            station['stop_node'] = sa_member['ref']
                                    break
                        
                        self.line['stations'][station['osmid']] = station
                    
                    route_point = dict()
                    route_point['node_id'] = member['ref']
                    route_point['order'] = route_point_order
                    route_point['distance_from_beginning'] = previous_route_point['distance_from_beginning']
                    route['route_points'][member['ref']] = route_point
                    route_point_order += 1
                elif 'stop' in member['role']:
                    logger.debug('Getting stop {0} info'.format(member['ref']))
                    
                    if member['ref'] not in route['route_points']:
                        if member['ref'] not in self.line['route_points']:
                            logger.debug("\t Not present, retrieving info...")
                            
                            osmstop = self.osmapi.NodeGet(member['ref'])
                            stop = dict()
                            stop['osmid'] = osmstop['id']
                            stop['latitude'] = osmstop['lat']
                            stop['longitude'] = osmstop['lon']
                            
                            self.line['route_points'][stop['osmid']] = stop
                        
                        current_point = self.line['route_points'][member['ref']]
                        if previous_point is not None :
                            previous_coords = [previous_point['latitude'], previous_point['longitude']]
                            current_coords = [current_point['latitude'], current_point['longitude']]
                            distance = int(vincenty(previous_coords, current_coords).meters)
                            distance_from_beginning += distance
                            
                        
                        route_point = dict()
                        route_point['node_id'] = member['ref']
                        route_point['order'] = route_point_order
                        route_point['distance_from_beginning'] = distance_from_beginning
                        route['route_points'][member['ref']] = route_point
                        route_point_order += 1
                        
                        previous_point = current_point
                        previous_route_point = route_point
                elif 'way' in member['type']:
                    logger.debug('Getting way {0} info'.format(member['ref']))
                    if member['ref'] not in ways:
                        logger.debug("\t Not present, retrieving info...")
                        way = self.osmapi.WayGet(member['ref'])
                        ways[member['ref']] = way
                    else:
                        way = ways[member['ref']]
                    
                    for node_id in way['nd']:
                        logger.debug('\tGetting node {0} info'.format(node_id))
                        
                        if node_id == 3773545143:
                            print("hola")
                        
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
                            previous_route_point = route_point
