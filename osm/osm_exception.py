class OSMRESTException(BaseException):
    def __init__(self, status_code):
        self.__messages = {'404' : 'The requested node does not exist',
                           '410' : 'The requested node has been deleted'}
        
        super(OSMRESTException, self).__init__(self.__messages[status_code])
