from .rest_client import RESTClient
from .osm_exception import OSMRESTException
from .osm_parser import OSMParser

class OSMClient:
    def get_osm_node_info(self, node_id):
        client = RESTClient()
        client.get(node_id)
        
        if client.hasErrorCode():
            exception = OSMRESTException(client.getStatusCode())
            raise exception
        
        parser = OSMParser()
        return parser.parse_node(client.content)
    
    def get_osm_route_info(self, route_id):
        client = RESTClient()
        client.get(route_id)
        
        if client.hasErrorCode():
            exception = OSMRESTException(client.getStatusCode())
            raise exception
        
        parser = OSMParser()
        return parser.parse_node(client.content)