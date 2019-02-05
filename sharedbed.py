from objects.linuxhost import LinuxHost
from objects.esxhost import EsxHost
from objects.windowshost import WindowsHost
from objects.trident import Trident
from objects.arena import Arena
from pprint import pprint
from flask import Flask
from flask_restful import Api, Resource, reqparse



if __name__ == "__main__":

    app = Flask(__name__)
    api =Api(app)

    api.add_resource(Arena, "/testbed/<string:target>")
    api.add_resource(Inventory, "/inventory/<string:target>")

    app.run(debug=True)

