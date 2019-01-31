from iohost import IOHost

class WindowsHost(IOHost):

    def __init__ (self, id, iqn):
        IOHost.__init__(self, id, iqn)
        self.os = 'windows'

    @property
    def os_type():
        return self.os

