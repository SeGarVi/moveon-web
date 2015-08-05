from .rest_client import RESTClient
from .osm_exception import OSMRESTException
from .osm_parser import OSMParser

class OSMClient:
    def getOsmNodeInfo(self, node_id):
        client = RESTClient()
        client.get(node_id)
        
        if client.hasErrorCode():
            exception = OSMRESTException(client.getStatusCode())
            raise exception
        
        parser = OSMParser()
        return parser.parse_node(client.content)