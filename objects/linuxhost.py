from iohost import IOHost

class LinuxHost(IOHost):

    def __init__ (self, id, iqn):
        IOHost.__init__(self, id, iqn)
        self.os = 'linux'

    @property
    def os_type():
        return self.os

