from xml.dom.minidom import parseString

from .osm_node import OsmNode
from .osm_relation import OsmRelation
from .osm_way import OsmWay

class OSMParser:
    def parse_node(self, unparsed_xml):
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
        shelter = False
        bench = False
        wheelchair= False
        for xml_tag in xml_tags:
            if u'name' in xml_tag.attributes[u'k'].value:
                name = xml_tag.attributes[u'v'].value
            if u'shelter'in xml_tag.attributes[u'k'].value:
                shelter = xml_tag.attributes[u'v'].value == u'yes'
            if u'bench'in xml_tag.attributes[u'k'].value:
                bench = xml_tag.attributes[u'v'].value == u'yes'
            if u'wheelchair'in xml_tag.attributes[u'k'].value:
                wheelchair = xml_tag.attributes[u'v'].value == u'yes'
        
        node = OsmNode(osm_id, latitude, longitude, name, shelter, bench, wheelchair)
        
        return node
    
    def parse_relation(self, unparsed_xml):
        dom = parseString(unparsed_xml)
        xml_node = dom.getElementsByTagName('relation')[0]
        xml_tags = dom.getElementsByTagName('tag')
        xml_members = dom.getElementsByTagName('member')
        
        osm_id = xml_node.attributes[u'id'].value
        
        if osm_id is None:
            raise SyntaxError(u'Malformed XML. Missing id.')
        
        name = ""
        colour = ""
        network = ""
        operator = ""
        from_ = ""
        to = ""
        ref = ""
        route = ""
        wheelchair= False
        for xml_tag in xml_tags:
            if u'name' in xml_tag.attributes[u'k'].value:
                name = xml_tag.attributes[u'v'].value
            if u'colour' in xml_tag.attributes[u'k'].value:
                colour = xml_tag.attributes[u'v'].value
            if u'network' in xml_tag.attributes[u'k'].value:
                network = xml_tag.attributes[u'v'].value
            if u'operator' in xml_tag.attributes[u'k'].value:
                operator = xml_tag.attributes[u'v'].value
            if u'from' in xml_tag.attributes[u'k'].value:
                from_ = xml_tag.attributes[u'v'].value
            if u'to' in xml_tag.attributes[u'k'].value:
                to = xml_tag.attributes[u'v'].value
            if u'ref' in xml_tag.attributes[u'k'].value:
                ref = xml_tag.attributes[u'v'].value
            if u'route' in xml_tag.attributes[u'k'].value:
                route = xml_tag.attributes[u'v'].value
            if u'wheelchair'in xml_tag.attributes[u'k'].value:
                wheelchair = xml_tag.attributes[u'v'].value == u'yes'
        
        relation = OsmRelation(id, colour, name, network, operator,
                           from_, to, ref, route, wheelchair)
        
        for xml_member in xml_members:
            if u'node' in xml_member.attributes[u'type'].value:
                relation.add_node_id(xml_member.attributes[u'ref'].value)
            elif u'relation' in xml_member.attributes[u'type'].value:
                relation.add_relation_id(xml_member.attributes[u'ref'].value)
            elif u'way' in xml_member.attributes[u'type'].value:
                relation.add_way_id(xml_member.attributes[u'ref'].value)
        
        return relation
    
    def parse_way(self, unparsed_xml):
        dom = parseString(unparsed_xml)
        xml_node = dom.getElementsByTagName('way')[0]
        xml_tags = dom.getElementsByTagName('tag')
        
        osm_id = xml_node.attributes[u'id'].value
        
        if osm_id is None:
            raise SyntaxError(u'Malformed XML. Missing id.')
        
        name = ""
        shelter = False
        bench = False
        wheelchair= False
        tram = False
        bus = False
        train = False
        for xml_tag in xml_tags:
            if u'name' in xml_tag.attributes[u'k'].value:
                name = xml_tag.attributes[u'v'].value
            if u'shelter'in xml_tag.attributes[u'k'].value:
                shelter = xml_tag.attributes[u'v'].value == u'yes'
            if u'bench'in xml_tag.attributes[u'k'].value:
                bench = xml_tag.attributes[u'v'].value == u'yes'
            if u'wheelchair'in xml_tag.attributes[u'k'].value:
                wheelchair = xml_tag.attributes[u'v'].value == u'yes'
            if u'tram'in xml_tag.attributes[u'k'].value:
                tram = xml_tag.attributes[u'v'].value == u'yes'
            if u'bus'in xml_tag.attributes[u'k'].value:
                bus = xml_tag.attributes[u'v'].value == u'yes'
            if u'train'in xml_tag.attributes[u'k'].value:
                train = xml_tag.attributes[u'v'].value == u'yes'
        
        way = OsmWay(id, name, bench, shelter, wheelchair, tram, bus, train)
        
        return way