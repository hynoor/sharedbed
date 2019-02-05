from objects.esxhost import EsxHost
from objects.windowshost import WindowsHost
from objects.trident import Trident
from objects.testbed import Testbed
from objects.inventory import StorageInventory, HostInventory
from pprint import pprint
from flask import Flask
from flask_restful import Api, Resource, reqparse



if __name__ == "__main__":

    app = Flask(__name__)
    api =Api(app)
    
    api.add_resource(Testbed, "/testbed/<string:target>")
    api.add_resource(StorageInventory, "/inventory/storage/<string:target>")
    api.add_resource(HostInventory, "/inventory/host/<string:target>")


    app.run(debug=True)

