import os, sys
from pprint import pprint
from flask_restful import Resource, reqparse
from resource_operator import ResourceOperator
from testbed_builder import TestbedBuilder


class Arena(Resource):
    """ All active testbed will be presented in arena
    """
    # a mapping between arrays to hosts
    mappings = dict()
    """
    {
        "WX-D05156"         : "10.109.211.231",
        "WX-D0515,WX-D0566" : "10.109.211.211,10.109.211.232",
        "WX-D0517,WX-D0518" : "10.109.211.11,10.109.211.31",
    }
    """
    operator = ResourceOperator()
    builder = TestbedBuilder()

    def get(self, target):
        if not self.operator.validate(target):
            return "Resource Not Found", 404
        if target in self.mappings.keys():
            return "Resource In Use: array:{} <---> hosts:{}".format(target, self.mappings[target]), 200
        names = target.split(',')
        for n in names:
            if not self.operator.inuse(n):
                return "Resource Available", 200
            else:
                for k, v in self.mappings.items():
                    if n in k:
                        return "Resource Inuse: array: {} hosts: {}".format(k, self.mappings[k]), 200


    def post(self, target):
        parser = reqparse.RequestParser()
        parser.add_argument("fc")
        parser.add_argument("num_windows")
        parser.add_argument("num_linux")
        parser.add_argument("num_esx")
        args = parser.parse_args()
        self.stats()
        if not self.operator.validate(target):
            return "Array Not Found", 404
        names = target.split(',')
        for n in names:
            if self.operator.inuse(n):
                return "Array Unavailable", 400
        # build hosts
        iohosts = []
        try:
            if args['num_linux']:
                if len(self.operator.linux_spare) >= int(args['num_linux']):
                    for _ in range(int(args['num_linux'])):
                        hostid = self.operator.linux_spare[0]
                        self.operator.switch(hostid, 'linux', True)
                        iohosts.append(hostid)
                else:
                    return "Linux Unvailable", 400
            if args['num_windows']:
                if len(self.operator.windows_spare) >= int(args['num_windows']):
                    for _ in range(int(args['num_windows'])):
                        hostid = self.operator.windows_spare[0]
                        self.operator.switch(hostid, 'windows', True)
                        iohosts.append(hostid)
                else:
                    return "Windows Unvailable", 400
            if args['num_esx']:
                if len(self.operator.esx_spare) >= int(args['num_esx']):
                    for _ in range(int(args['num_esx'])):
                        hostid = self.operator.esx_spare[0]
                        self.operator.switch(hostid, 'esx', True)
                        iohosts.append(hostid)
                else:
                    return "ESXi Unvailable", 400
            for n in names:
                self.operator.switch(n, 'storage', True)
            self.mappings[target] = iohosts
        except ValueEroperatorr as e:
            return "ValueEroperatorr: {}".format(e), 500
        
        # build testbed xml file
        fchosts = []
        for id in target.split(','):
            vip = self.operator.lookup_storage(id).vcenter_id
            fchosts.append(self.operator.lookup_storage(id).fc_hosts)
        vcenter = vip
        builder = TestbedBuilder(array=target, vcenter=vip, iscsi_host=",".join(iohosts), fc_host=",".join(fchosts))
        testbed = builder.build()
        return unicode(testbed), 200


    def put(self, target):
        pass


    def delete(self, target):
        self.stats()
        if not self.operator.validate(target) or not self.mappings.keys():
            return "Resource Not Found", 404
        names = target.split(',')
        for n in names:
            if self.operator.inuse(n):
                self.operator.switch(n, 'storage', False)
            else:
                return "Resource Not Found", 404
        for n in self.mappings[target]:
            if n in self.operator.linux_inuse:
                self.operator.switch(n, 'linux', False)
            elif n in self.operator.windows_inuse:
                self.operator.switch(n, 'windows', False)
            elif n in self.operator.esx_inuse:
                self.operator.switch(n, 'esx', False)
            else:
                return "Host Not Found", 404
        del self.mappings[target]
        return "Resource Released", 200


    def stats(self):
        print('------------storage------------------')
        pprint(self.operator.storage_inuse)
        print('-------------------------------------')
        print('-------------linux-------------------')
        pprint(self.operator.linux_inuse)
        print('-------------------------------------')
        print('------------windwos------------------')
        pprint(self.operator.windows_inuse)
        print('-------------------------------------')
        print('---------spare storage---------------')
        pprint(self.operator.storage_spare)
        print('-------------------------------------')
        print('----------spare linux----------------')
        pprint(self.operator.linux_spare)
        print('-------------------------------------')
        print('----------spare windows--------------')
        pprint(self.operator.windows_spare)
        print('-------------------------------------')
        print('------------mapping------------------')
        pprint(self.mappings)
        print('-------------------------------------')
























