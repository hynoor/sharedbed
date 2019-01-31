from storage import Storage
from vcenter import VCenter

class Trident(Storage):

    def __init__ (self, id, fchosts, vcenters):
        Storage.__init__(self, id, fchosts)
        self.vcenters = []

        for vc in vcenters:
            self.vcenters.append(VCenter(vcenter))

    @property
    def vcenters():
        return self.vcenters

