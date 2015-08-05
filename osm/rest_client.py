import httplib2

class RESTClient:
    def __init__(self):
        self._error_codes = ['404', '410']
    
    def get(self, node_id):
        http_client = httplib2.Http()
        url = 'http://api.openstreetmap.org/api/0.6/node/' + node_id
        self._response, self.content = http_client.request(url)
    
    def hasErrorCode(self):
        return self._response['status'] in self._error_codes
    
    def getStatusCode(self):
        return self._response['status']