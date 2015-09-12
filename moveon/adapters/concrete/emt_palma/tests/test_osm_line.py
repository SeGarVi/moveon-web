from moveon.adapters.tests.osm_line_test import OSMLineTest
from moveon.adapters.concrete.emt_palma.static.osm_line import OSMLine

class EMTPalmaOSMLineTest(OSMLineTest):
    def setUp(self):
        self.concrete_class = OSMLine
        self.osmid = '5437366'
        
        super(EMTPalmaOSMLineTest, self).setUp()
    
    def test_static_adapter(self):
        """The initialized line has the mandatory fields"""
        super(EMTPalmaOSMLineTest, self).static_adapter_check()