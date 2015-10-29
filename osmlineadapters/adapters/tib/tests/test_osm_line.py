from osmlineadapters.tests.osm_line_test import OSMLineTest
from osmlineadapters.adapters.tib.osm_line import OSMLine

class TIBOSMLineTest(OSMLineTest):
    def setUp(self):
        self.concrete_class = OSMLine
        self.osmid = '5613738'
        
        super(TIBOSMLineTest, self).setUp()
    
    def test_static_adapter(self):
        """The initialized line has the mandatory fields"""
        super(TIBOSMLineTest, self).static_adapter_check()
