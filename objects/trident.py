from storage import Storage
from vcenter import VCenter

class Trident(Storage):

    def __init__ (self, id, fchosts, vcenter):
        Storage.__init__(self, id, fchosts)
        self.vcenter = VCenter(vcenter)
        self.vcenter_id = vcenter

    @property
    def vcenter():
        return self.vcenter

    @property
    def vcenter_id():
        return self.vcenter_id
