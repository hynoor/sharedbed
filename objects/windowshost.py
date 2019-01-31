from iohost import IOHost

class WindowsHost(IOHost):

    def __init__ (self, id, iqn):
        IOHost.__init__(self, id, iqn)


    @property
    def os_type():
        return 'windows'

