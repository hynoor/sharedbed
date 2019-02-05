import os, sys
import flask
from pprint import pprint
from flask import Response
from flask import make_response
from flask_restful import Resource, reqparse
from resource_operator import ResourceOperator


class Inventory(Resource):
    operator = ResourceOperator()

    def get(self, target):
        pass


    def post(self, target):
        parser = reqparse.RequestParser()
        parser.add_argument("vcenter")
        parser.add_argument("fc_hosts")
        args = parser.parse_args()
        try:
            if target:
                self.operator.add_storage(target, args)
        except Exception:
            return "Internal Error: {}".format(e), 500
             
        return "Inventory Added", 200


    def put(self, target):
        pass


    def delete(self, target):
        if not self.operator.validate(target):
            return "Resource Not Found", 404

        del self.operator.remvove_storage


    
    @property
    def report(self):
        output = "Storage Available: {}  {}\n".format(len(self.operator.storage_spare), self.operator.storage_spare)
        output += "Linux Host Available: {}  {}".format(len(self.operator.linux_spare), self.operator.linux_spare)
        return output

