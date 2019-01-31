from host import Host

class IOHost(Host):

    def __init__ (self, id, iqn):
        Host.__init__(self, id)
        if iqn:
            self.iqn = iqn

    @property
    def iqn():
        return self.iqn
