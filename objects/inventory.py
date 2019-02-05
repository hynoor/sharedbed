import os, sys
import flask
import settings
from pprint import pprint
from flask import Response
from flask import make_response
from flask_restful import Resource, reqparse
from resource_operator import ResourceOperator


class StorageInventory(Resource):

    operator = settings.resource_operator

    def get(self, target):
        pass


    def post(self, target):
        parser = reqparse.RequestParser()
        parser.add_argument("vcenter")
        parser.add_argument("fc_hosts")
        args = parser.parse_args()
        try:
            if target:
                self.operator.add_storage(target, args['vcenter'], args['fc_hosts'])
            else:
                return "ERROR: Storage Name Missing", 404
        except Exception as e:
            return "ERROR: Internal Server Error: {}".format(e), 500
        return "Storage Inventory Updated", 200


    def put(self, target):
        pass


    def delete(self, target):
        try:
            if target not in self.operator.storage_resources.keys():
                return "ERROR: Storage Inventory Not Found", 404
            self.operator.remove_storage(target)
        except Exception as e:
            return "ERROR: Internal Server Error: {}".format(e), 500

        return "Storage Inventory Removed", 200
   


class HostInventory(Resource):

    operator = settings.resource_operator

    def get(self, target):
        pass


    def post(self, target):
        parser = reqparse.RequestParser()
        parser.add_argument("iqn")
        parser.add_argument("os")
        args = parser.parse_args()
        try:
            if target and args['os']:
                self.operator.add_host(target, args['iqn'], args['os'])
            else:
                return "ERROR: Required Argument Missing", 400
        except Exception as e:
            return "Internal Error: {}".format(e), 500
        return "Host Inventory Updated", 200


    def put(self, target):
        pass


    def delete(self, target):
        try:
            if target not in self.operator.iohost_resources.keys():
                return "ERROR: Inventory Not Found", 404
            self.operator.remove_host(target)
        except Exception as e:
            return "ERROR: Internal Server Error: {}".format(e), 500

        return "Host Inventory Removed", 200
   

    @property
    def report(self):
        output = "Storage Available: {}  {}\n".format(len(self.operator.storage_spare), self.operator.storage_spare)
        output += "Linux Host Available: {}  {}".format(len(self.operator.linux_spare), self.operator.linux_spare)
        return output

