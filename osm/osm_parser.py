from xml.dom.minidom import parseString

from .osm_node import OsmNode

class OSMParser:
    def parse_node(self, unparsed_xml):
        """  <node id="123" lat="..." lon="..." version="142" changeset="12" user="fred" uid="123" visible="true" timestamp="2005-07-30T14:27:12+01:00"> """
        dom = parseString(unparsed_xml)
        xml_node = dom.getElementsByTagName('node')[0]
        xml_tags = dom.getElementsByTagName('tag')
        
        osm_id = xml_node.attributes[u'id'].value
        latitude = xml_node.attributes[u'lat'].value
        longitude = xml_node.attributes[u'lon'].value
        
        if osm_id is None:
            raise SyntaxError(u'Malformed XML. Missing id.')
        if latitude is None:
            raise SyntaxError(u'Malformed XML. Missing latitude.')
        if longitude is None:
            raise SyntaxError(u'Malformed XML. Missing longitude.')
        
        name = ""
        for xml_tag in xml_tags:
            if u'name' in xml_tag.attributes[u'k'].value:
                name = xml_tag.attributes[u'v'].value
        
        node = OsmNode(osm_id, latitude, longitude, name)
        
        return node