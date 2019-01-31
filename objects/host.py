from sharedresource import SharedResource

class Host(SharedResource):

    def __init__ (self, id):
        SharedResource.__init__(self, id)

