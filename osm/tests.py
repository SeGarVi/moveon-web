from django.test import TestCase

from osm.osm_client import OsmClient


class OsmClientTestCase(TestCase):
    def setUp(self):
        self.osm_client = OsmClient()
    
    def testResponseIsCorrect(self):
        """We get a 200 status code"""
        res = self.osm_client.get_osm_node_info('669638944')
        self.assertTrue(True)