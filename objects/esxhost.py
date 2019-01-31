from iohost import IOHost

class EsxHost(IOHost):

    def __init__ (self, id, iqn):
        IOHost.__init__(self, id, iqn)


    @property
    def os_type():
        return 'esx'

