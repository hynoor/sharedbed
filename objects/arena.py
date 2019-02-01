import os, sys
from collections import defaultdict
from objects.linuxhost import LinuxHost
from objects.esxhost import EsxHost
from objects.windowshost import WindowsHost
from objects.trident import Trident
from flask_restful import Resource, reqparse
from pprint import pprint


class ResourceManager():
    """ Reource Manager manage the dynamic testbed records
    """

    def __init__(self, storage_res='./resources/arrays.csv', host_res='./resources/iohosts.csv'):
        self.storages =  self.load_resource(storage_res)
        self.iohosts =  self.load_resource(host_res)
        self.iohost_resources = dict()
        self.storage_resources = dict()

        self.storage_bitmap = defaultdict(lambda: False)
        self.linux_bitmap = defaultdict(lambda: False)
        self.windows_bitmap = defaultdict(lambda: False)
        self.esx_bitmap = defaultdict(lambda: False)

        for h in self.iohosts:
            if h['os'] == 'linux':
                self.iohost_resources[h['id']] = LinuxHost(h['id'], h['iqn'])
                self.linux_bitmap[h['id']] = False
            elif h['os'] == 'esx':
                self.iohost_resources[h['id']] = EsxHost(h['id'], h['iqn'])
                self.esx_bitmap[h['id']] = False
            elif h['os'] == 'windows':
                self.iohost_resources[h['id']] = WindowsHost(h['id'], h['iqn'])
                self.windows_bitmap[h['id']] = False
            else:
                print("WARN: Ignored nnsupported OS type!")

        for a in self.storages:
            self.storage_resources[a['id']] = Trident(a['id'], a['fc_hosts'], a['vcenter'])
            self.storage_bitmap[a['id']] = False


    def load_resource(self, resource):
        import csv
        reader = csv.reader(open(resource, 'r'))
        header = reader.next()
        resources = []

        for row in reader:
            res = {}
            for idx, h in enumerate(header, 0):
                res[h] = row[idx]
            resources.append(res)
        return resources

    def inuse(self, id):
        if id in self.storage_bitmap.keys():
            return self.storage_bitmap[id]
        if id in self.linux_bitmap.keys():
            return self.linux_bitmap[id]
        if id in self.esx_bitmap.keys():
            return self.esx_bitmap[id]
        if id in self.windows_bitmap.keys():
            return self.windows_bitmap[id]


    def switch(self, id, type, status):
        if type == 'storage':
            self.storage_bitmap[id] = status
            return True
        if type == 'linux':
            self.linux_bitmap[id] = status
            return True
        elif type == 'esx':
            self.esx_bitmap[id] = status
            return True
        elif type == 'windows':
            self.windows_bitmap[id] = status
            return True
        else:
            return False

    
    def validate(self, target):
        for t in target.split(','):
            print self.storages
            if t not in self.storage_bitmap.keys():
                return False
        return True

            
            
        

    @property
    def storage_inuse(self):
        return [(k) for k in self.storage_bitmap.keys() if self.storage_bitmap[k]]

    @property
    def storage_spare(self):
        return [(k) for k in self.storage_bitmap.keys() if not self.storage_bitmap[k]]

    @property
    def linux_inuse(self):
        return [(k) for k in self.linux_bitmap.keys() if self.lnux_bitmap[k]]

    @property
    def linux_spare(self):
        return [(k) for k in self.linux_bitmap.keys() if not self.linux_bitmap[k]]


rm = ResourceManager()

class Arena(Resource):
    """ All active testbed will be presented in arena
    """
    global rm 

    def get(self, target):
        if not rm.validate(target):
            return "Resource Not Found", 200
        names = target.split(',')
        for n in names:
            pprint(rm.storage_bitmap) 
            if rm.inuse(n):
                return "Resource In-use", 200
        # grab a iohost
        if len(rm.linux_spare):
            rm.switch(rm.linux_spare[0], 'linux', True)
            for n in names:
                rm.switch(n, 'storage', True)
            pprint(rm.storage_bitmap) 
            return "Resource Found", 200
        else:
            pprint(rm.storage_bitmap) 
            return "Host Resource unvailable", 200


    def post(self, target):
        pass


    def put(self, target):
        pass


    def delete(self, target):
        pass



