from host import Host

class IOHost(Host):

    def __init__ (self, id, iqn=None):
        Host.__init__(self, id)
        if iqn:
            self.iqn = iqn

    @property
    def iqn():
        return self.iqn
