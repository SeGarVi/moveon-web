from django.test import TestCase

class OSMLineTest(TestCase):
    def setUp(self):
        print("\n\nRunning adapter test for {0}.{1} with OSM Line id {2}\n\n"
            .format(self.concrete_class.__module__, self.concrete_class.__name__, self.osmid))
        
        try:
            self.concrete_instance = self.concrete_class(self.osmid)
        except:
            self.fail("Error when initializing")
    
    def static_adapter_check(self):
        self._line_has_correct_values()
        self._route_has_correct_values()
        self._station_has_correct_values()
        self._route_point_has_correct_values()
        self._route_point_references_exist()
        self._station_references_exist()
    
    def _line_has_correct_values(self):
        """The initialized line has the mandatory fields"""
        self.assertIsNotNone(self.concrete_instance.line)
        
        line = self.concrete_instance.line
        
        self.assertTrue('osmid' in line)
        self.assertTrue('company' in line)
        self.assertTrue('transport' in line)
        self.assertTrue('code' in line)
        self.assertTrue('name' in line)
        self.assertTrue('colour' in line)
        self.assertTrue('stations' in line)
        self.assertTrue('route_points' in line)
        self.assertTrue('routes' in line)
        
        self.assertTrue(type(line['osmid']) is int)
        self.assertTrue(type(line['company']) is str)
        self.assertTrue(type(line['transport']) is str)
        self.assertTrue(type(line['code']) is str)
        self.assertTrue(type(line['name']) is str)
        self.assertTrue(type(line['colour']) is str)
        self.assertTrue(type(line['stations']) is dict)
        self.assertTrue(type(line['route_points']) is dict)
        self.assertTrue(type(line['routes']) is dict)
        
        self.assertIsNotNone(line['company'])
        self.assertIsNotNone(line['transport'])
        self.assertIsNotNone(line['code'])
        self.assertIsNotNone(line['name'])
        self.assertIsNotNone(line['colour'])
        self.assertIsNotNone(line['stations'])
        self.assertIsNotNone(line['route_points'])
        self.assertIsNotNone(line['routes'])
        
        self.assertNotEqual(line['osmid'], "")
        self.assertNotEqual(line['company'], "")
        self.assertNotEqual(line['transport'], "")
        self.assertNotEqual(line['code'], "")
        self.assertNotEqual(line['name'], "")
        self.assertNotEqual(line['colour'], "")
        
        self.assertGreaterEqual(len(line['stations'].values()), 0)
        self.assertGreaterEqual(len(line['route_points'].values()), 0)
        self.assertGreaterEqual(len(line['routes'].values()), 0)
    
    def _route_has_correct_values(self):
        """The initialized routes have the mandatory fields"""
        for route in self.concrete_instance.line['routes'].values():
            self.assertTrue('osmid' in route)
            self.assertTrue('name' in route)
            self.assertTrue('station_from' in route)
            self.assertTrue('station_to' in route)
            self.assertTrue('route_points' in route)
             
            self.assertTrue(type(route['osmid']) is int)
            self.assertTrue(type(route['name']) is str)
            self.assertTrue(type(route['station_from']) is str)
            self.assertTrue(type(route['station_to']) is str)
            self.assertTrue(type(route['route_points']) is list)
             
            self.assertIsNotNone(route['name'])
            self.assertIsNotNone(route['station_from'])
            self.assertIsNotNone(route['station_to'])
            self.assertIsNotNone(route['route_points'])
             
            self.assertNotEqual(route['name'], "")
            self.assertNotEqual(route['station_from'], "")
            self.assertNotEqual(route['station_to'], "")
             
            self.assertGreaterEqual(len(route['route_points']), 0)
     
    def _station_has_correct_values(self):
        """The initialized stations have the mandatory fields"""
        for station in self.concrete_instance.line['stations'].values():
            self.assertTrue('osmid' in station)
            self.assertTrue('latitude' in station)
            self.assertTrue('longitude' in station)
            self.assertTrue('code' in station)
            self.assertTrue('name' in station)
            self.assertTrue('available' in station)
             
            self.assertTrue(type(station['osmid']) is int)
            self.assertTrue(type(station['latitude']) is float)
            self.assertTrue(type(station['longitude']) is float)
            self.assertTrue(type(station['code']) is str)
            self.assertTrue(type(station['name']) is str)
            self.assertTrue(type(station['available']) is bool)
            self.assertTrue(station['adapted'] is None or type(station['adapted']) is bool)
            self.assertTrue(station['shelter'] is None or type(station['shelter']) is bool) 
            self.assertTrue(station['bench'] is None or type(station['bench']) is bool)
             
            self.assertIsNotNone(station['code'])
            self.assertIsNotNone(station['name'])
             
            self.assertNotEqual(station['code'], "")
            self.assertNotEqual(station['name'], "")
     
    def _route_point_has_correct_values(self):
        """The initialized route points have the mandatory fields"""
        for route_point in self.concrete_instance.line['route_points'].values():
            self.assertTrue('osmid' in route_point)
            self.assertTrue('latitude' in route_point)
            self.assertTrue('longitude' in route_point)
             
            self.assertTrue(type(route_point['osmid']) is int)
            self.assertTrue(type(route_point['latitude']) is float)
            self.assertTrue(type(route_point['longitude']) is float)
     
    def _route_point_references_exist(self):
        """The referenced route points in a route exist in the line"""
        line = self.concrete_instance.line
        for route in self.concrete_instance.line['routes'].values():
            for route_point in route['route_points']:
                self.assertTrue('node_id' in route_point)
                self.assertTrue('order' in route_point)
                 
                self.assertTrue(type(route_point['node_id']) is int)
                self.assertTrue(type(route_point['order']) is int)
                 
                self.assertGreaterEqual(route_point['order'], 0)
                 
                self.assertTrue(route_point['node_id'] in line['route_points'])
     
    def _station_references_exist(self):
        """The referenced stations in a route point exist in the line"""
        line = self.concrete_instance.line
        for route_point in line['route_points'].values():
            if 'near_station' in route_point:
                self.assertTrue(type(route_point['near_station']) is int)
                self.assertTrue(route_point['near_station'] in line['stations'])
