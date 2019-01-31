from sharedresource import SharedResource
from iohost import IOHost

class Storage(SharedResource):

    def __init__ (self, id, fchosts):
        SharedResource.__init__(self, id)
        self.fc_hosts = []

        for fc_host in fchosts:
            self.fc_hosts.append(IOHosts(fchosts))

    @property
    def fc_hosts():
        return self.fc_hosts

