import json

class AbstractOSMLine():
    def __init__(self):
        self.line = dict()
    
    def to_json(self):
        return json.dumps(self.line)
    
    def to_simplified_json(self):
        simplified_line = dict()
        
        simplified_line['osmid'] = self.line['osmid']
        simplified_line['company'] = self.line['company']
        simplified_line['transport'] = self.line['transport']
        simplified_line['code'] = self.line['code']
        simplified_line['name'] = self.line['name']
        simplified_line['colour'] = self.line['colour']
        simplified_line['routes'] = []
        
        for route in self.line['routes'].values():
            simplified_route = dict()
            simplified_route['osmid'] = route['osmid']
            simplified_route['name'] = route['name']
            simplified_route['station_from'] = route['station_from']
            simplified_route['station_to'] = route['station_to']
            simplified_route['stations'] = []
            
            station_order = 0
            for route_point_ref in sorted(route['route_points'], key=lambda x: x['order']):
                route_point = self.line['route_points'][route_point_ref['node_id']]
                if 'near_station' in route_point:
                    station_order += 1
                    
                    station = self.line['stations'][route_point['near_station']]
                    simplified_station = dict()
                    simplified_station['osmid'] = station['osmid']
                    simplified_station['latitude'] = station['latitude']
                    simplified_station['longitude'] = station['longitude']
                    simplified_station['code'] = station['code']
                    simplified_station['name'] = station['name']
                    simplified_station['available'] = station['available']
                    simplified_station['adapted'] = station.get('adapted')
                    simplified_station['shelter'] = station.get('shelter')
                    simplified_station['bench'] = station.get('bench')
                    simplified_station['order'] = station_order
                    
                    simplified_route['stations'].append(simplified_station)
            
            simplified_line['routes'].append(simplified_route)
                    
        return json.dumps(simplified_line)
