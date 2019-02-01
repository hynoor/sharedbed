from storage import Storage
from vcenter import VCenter

class Trident(Storage):

    def __init__ (self, id, fchosts, vcenter):
        Storage.__init__(self, id, fchosts)
        self.vcenter = VCenter(vcenter)

    @property
    def vcenter():
        return self.vcenter

