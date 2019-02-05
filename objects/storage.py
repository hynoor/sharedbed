from sharedresource import SharedResource
from iohost import IOHost

class Storage(SharedResource):

    def __init__ (self, id, fchosts):
        SharedResource.__init__(self, id)
        self.fc_hosts = []
        self.fc_host_objs = []
        if fchosts: 
            for fc_host in fchosts.split(','):
                self.fc_host_objs.append(IOHost(fc_host))
                self.fc_hosts.append(fc_host)

    @property
    def fc_host_objs():
        return self.fc_host_objs

    @property
    def fc_hosts():
        return self.fc_hosts
