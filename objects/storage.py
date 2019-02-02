from sharedresource import SharedResource
from iohost import IOHost

class Storage(SharedResource):

    def __init__ (self, id, fchosts):
        SharedResource.__init__(self, id)
        self.fc_hosts = fchosts
        self.fc_host_objs = []

        for fc_host in fchosts:
            self.fc_host_objs.append(IOHost(fc_host))

    @property
    def fc_host_objs():
        return self.fc_host_objs

    @property
    def fc_hosts():
        return self.fc_hosts
