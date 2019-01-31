from objects.linuxhost import LinuxHost
from objects.esxhost import EsxHost
from objects.windowshost import WindowsHost
from objects.trident import Trident
from pprint import pprint

def load_hosts():
    hosts = [{
        'id'  : '10.229.14.201',
        'iqn' : None,
        'os'  : 'linux',
    }]

    return hosts

def load_arrays():
    arrays = [{
        'id'      : 'WX-D6031',
        'fc_hosts' : [],
        'vcenters' : [],
    }]

    return arrays

if __name__ == "__main__":

    dancers = []
    arraypool = []
    hostpool = []

    hosts = load_hosts()
    arrays = load_arrays()

    for h in hosts:
        if h['os'] == 'linux':
            hostpool.append(LinuxHost(h['id'], h['iqn']))
        elif h['os'] == 'esx':
            hostpool.append(EsxHost(h['id'], h['iqn']))
        elif h['os'] == 'windows':
            hostpool.append(WindowsHost(h['id'], h['iqn'], h['os']))
        else:
            print("ERROR: Unsupported OS type!")

    for a in arrays:
        arraypool.append(Trident(a['id'], a['fc_hosts'], a['vcenters']))

    pprint(hostpool)
    pprint(arraypool)

