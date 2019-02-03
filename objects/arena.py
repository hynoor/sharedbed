import os, sys
import flask
from pprint import pprint
from flask import Response
from flask import make_response
from flask_restful import Resource, reqparse
from resource_operator import ResourceOperator
from testbed_builder import TestbedBuilder


class Arena(Resource):
    """ All active testbed will be presented in arena
    """
    # a mapping between arrays to hosts
    mappings = dict()
    """
    sample data structure:
    {
        "WX-D05156"         : "10.109.211.231",
        "WX-D0515,WX-D0566" : "10.109.211.211,10.109.211.232",
        "WX-D0517,WX-D0518" : "10.109.211.11,10.109.211.31",
    }
    """
    operator = ResourceOperator()
    builder = TestbedBuilder()

    def get(self, target):
        if target == 'stats':
            return self.report, 200
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
        parser.add_argument("type")
        parser.add_argument("windows")
        parser.add_argument("linux")
        parser.add_argument("esx")
        parser.add_argument("fc")
        args = parser.parse_args()
        self.stats()
        if not self.operator.validate(target):
            return "Array Not Found", 404
        names = target.split(',')
        for n in names:
            if self.operator.inuse(n):
                return "Array Unavailable", 400
        # build hosts
        build_params = dict()
        linux_iohosts = []
        windows_iohosts = []
        esx_iohosts = []
        fc_iohosts = []
        try:
            if args['type']:
                build_params['type'] = args['type'].lower()
            if args['linux']:
                if len(self.operator.linux_spare) >= int(args['linux']):
                    for i in range(int(args['linux'])):
                        hostid = self.operator.linux_spare[i]
                        #self.operator.switch(hostid, 'linux', True)
                        linux_iohosts.append(hostid)
                    if len(linux_iohosts) > 0:
                        build_params['linux_host'] = ",".join(linux_iohosts)
                    elif int(args['linux']) == 0:
                        pass
                else:
                    return "Linux Unvailable", 400
            if args['windows']:
                if len(self.operator.windows_spare) >= int(args['windows']):
                    for i in range(int(args['windows'])):
                        hostid = self.operator.windows_spare[i]
                        #self.operator.switch(hostid, 'windows', True)
                        windows_iohosts.append(hostid)
                    if len(windows_iohosts) > 0:
                        build_params['windows_host'] = ",".join(windows_iohosts)
                    elif int(args['windows']) == 0:
                        pass
                else:
                    return "Windows Unvailable", 400
            if args['esx']:
                if len(self.operator.esx_spare) >= int(args['esx']):
                    for i in range(int(args['esx'])):
                        hostid = self.operator.esx_spare[i]
                        #self.operator.switch(hostid, 'esx', True)
                        esx_iohosts.append(hostid)
                    if len(esx_iohosts) > 0:
                        build_params['esx_host'] = ",".join(esx_iohosts)
                    elif int(args['esx']) == 0:
                        pass
                else:
                    return "ESXi Unvailable", 400
            if args['fc']:
                for name in names:
                    for id in self.operator.lookup_storage(name).fc_hosts.split(','):
                        if id != '':
                            fc_iohosts.append(id)
                if len(fc_iohosts) > 0:
                    build_params['fc_host'] = ",".join(fc_iohosts)
                elif int(args['fc']) == 0:
                    pass
                else:
                    return "FC Unvailable", 400
                if len(fc_iohosts) < int(args['fc']):
                    return "FC Unvailable", 400
            # commit operations
            for n in names:
                self.operator.switch(n, 'storage', True)
            for n in linux_iohosts:
                self.operator.switch(n, 'linux', True)
                print("operation host: {}".format(n))
            for n in windows_iohosts:
                self.operator.switch(n, 'windows', True)
            for n in esx_iohosts:
                self.operator.switch(n, 'esx', True)
            self.mappings[target] = linux_iohosts + windows_iohosts + esx_iohosts
        except ValueError as e:
            return "ValueEroperatorr: {}".format(e), 500
        
        # build testbed xml file
        for id in target.split(','):
            vip = self.operator.lookup_storage(id).vcenter_id
        vcenter = vip
        try:
            builder = TestbedBuilder(array=target, vcenter=vcenter, kwargs=build_params)
            response = builder.build()
        except Exception as e:
            # rollback
            self.delete(target) 
            return "Server Internal Error: {}".format(e), 500

        return Response(response, mimetype='text/xml')


    def put(self, target):
        pass


    def delete(self, target):
        if target in self.mappings.keys():
            for n in target.split(','):
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
    
    @property
    def report(self):
        output = "Storage Available: {}  {}\n".format(len(self.operator.storage_spare), self.operator.storage_spare)
        output += "Linux Host Available: {}  {}".format(len(self.operator.linux_spare), self.operator.linux_spare)
        return output


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
























