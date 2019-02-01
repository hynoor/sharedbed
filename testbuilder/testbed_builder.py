#! python testbed_builder.py
import os,sys,re,getopt,subprocess
from xml.dom import minidom
from xml.etree.ElementTree import (
        Element, SubElement, Comment, tostring,
)
from pprint import pprint

def get_cyc_config(path):
    """ Read the cyc_config file from given path
    """
    configs= dict()
    if not os.path.exists(path):
        print("ERR: Given cyc-config-path: %s doesn't exist!" % path)
        exit(-1)
    with open(path, 'r') as fh:
        for line in fh.readlines():
            items = re.findall('^export (\w+)="(.+)"$', line)
            if items:
                for group in items:
                    configs[group[0]] = group[1]
    if configs:
        return configs
    else:
        print("ERR: malform cyc_config file given, none configuration got!")
        exit(-1)

def terminal_info(trident):
    """ get terminal info (IP and Port)
    """
    swarm = False
    try:
        res = subprocess.check_output(["swarm", trident])
        swarm = True
    except OSError as e:
        print("WRN: current host doesn't support swarm-cli, user need manually update the termanial IPs and ports!")
        return (False, False)
    ta = re.findall('Terminal SPA: (\S+) (\d+)', res)
    tb = re.findall('Terminal SPB: (\S+) (\d+)', res)
    terminala = dict()
    terminalb = dict()
    if ta and tb:
        for tagrp, tbgrp in zip(ta, tb):
            terminala['ip'] = tagrp[0]
            terminala['port'] = tagrp[1]
            terminalb['ip'] = tbgrp[0]
            terminalb['port'] = tbgrp[1]

    return (terminala, terminalb)


def usage():
    print("\ntestbed-builder - a trident testbed xml builder\n")
    print("python testbed_builder.py <OPTIONs>")
    OPT = "\n"
    OPT += "OPTIONs:\n\n"
    OPT += "        --trident         : (Required) Target Trident system names, support muliple names which separated by comma, ex:WX-D0515,WX-D0516\n"
    OPT += "        --deploy-type     : (Optional) Type of deploy, valid values: HCI|SAN (default: SAN)\n"
    OPT += "        --iscsi-host      : (Optional) Host IP(s) used for iSCSI I/O, accepts multiple IPs which separated by comma, ex:0.111.112.222,10.111.112.232\n"
    OPT += "        --fc-host         : (Optional) Host IP(s) used for FC I/O, accepts multiple IPs which separated bycomma, ex:0.111.112.222,10.111.112.232\n"
    OPT += "        --vcenter         : (Optional) vCenter IP used for HCI testbed creation\n"
    OPT += "        --cyc-config-dir  : (Optional) Base folder path of cyc_configs \n"
    OPT += "        --output          : (Optional) Path to saving the testbed xml file\n\n"

    print(OPT)
    print("Example:\n# python testbed_builder.py --trident WX-D0515,WX-D0516 --deploy-type HCI --vcenter 10.111.244.43 --iscsi-host 10.111.223.110 --fc-host 10.111.142.109 --output ./DevOps-WX-D0515_WX-D0516.xml\n")

if __name__ == '__main__':

    if len(sys.argv) == 1:
        usage()
        sys.exit(-1)

    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 
            'h:', [
                  'help',
                  'trident=', 
                  'deploy-type=', 
                  'iscsi-host=',
                  'fc-host=',
                  'vcenter=',
                  'cyc-config-dir=',
                  'output=',
                  ]
        )
    except getopt.GetoptError as e:
        # print help information and exit:
        sys.exit("Error: Parameter error: %s" % str(e))

    input_info = {
            'deploy-type' : 'SAN',
            'cyc-config-dir' : '/opt/share/DevOpsCIT/configuration/devops-ctee-config/cyc_configs/'
            }
    for o, a in opts:
        if o in ('--trident'):
            input_info[o[2:]] = a  
        elif o in ('--deploy-type'):
            input_info[o[2:]] = a  
        elif o in ('--iscsi-host'):
            input_info[o[2:]] = a  
        elif o in ('--fc-host'):
            input_info[o[2:]] = a  
        elif o in ('--vcenter'):
            input_info[o[2:]] = a  
        elif o in ('--cyc-config-dir'):
            input_info[o[2:]] = a  
        elif o in ('--output'):
            input_info[o[2:]] = a  
        else:
            usage()
            exit(-1)
    # starts to build
    if (input_info['deploy-type'] == 'HCI') and ('vcenter' not in input_info):
        print("ERR: parameter 'vcenter' is must when 'deploy-type' is HCI!")
        exit(-1)

    root = Element('testbedinfo')
    root.set('version', '1.0')
    root.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
    root.set('xmlns:xsd', "http://www.w3.org/2001/XMLSchema")
    root.set('doc_type', "testbed")

    cyclones= SubElement(root, 'cyclones')
    if input_info['trident'] is '':
        print('ERR: parameter "vcenter" is required when delopy-type is HCI!')
        exit(-1)
    else:
        for system_name in input_info['trident'].split(','):
            cyc_config_path = os.path.join(input_info['cyc-config-dir'], 'cyc-cfg.txt.' + system_name)
            config = get_cyc_config(cyc_config_path)
            cyclone = SubElement(cyclones, 'cyclone')
            cyclone.set('name', system_name)
            if input_info['deploy-type'] == 'HCI':
                cyclone.set('datacenter_name', 'DataCenter' + system_name[2:] )
                cyclone.set('name', 'Cluster' + system_name[2:] )
                cyclone.set('vcenter', input_info['vcenter'])
            # build management_info
            management_info = SubElement(cyclone, 'management_info')
            management_info.set('management_ip_addr', config['cluster_ip'])
            # build appliances
            appliances = SubElement(cyclone, 'appliances')
            appliance = SubElement(appliances, 'appliance')
            appliance.set('id', system_name)
            appliance.set('ip_address', config['appliance_ip'])
            if 'cyc-config-path' in input_info:
                appliance.set('cyc_config', input_info['cyc-config-path'])
            else: # default path
                appliance.set('cyc_config', cyc_config_path)

            ta, tb = terminal_info(system_name)

            # build nodes
            nodes = SubElement(appliance, 'nodes')
            # build node-a
            node = SubElement(nodes, 'node')
            node.set('id', 'a')
            cyclone_controller = SubElement(node, 'cyclone_controller')
            cyclone_controller.set('id', system_name + '-a')
            if input_info['deploy-type'] == 'HCI':
                hypervisor_host = SubElement(node, 'hypervisor_host')
                hypervisor_host.set('id', system_name + '-HOST-1')
            terminal = SubElement(node, 'terminal')
            if ta is False:
                terminal.set('ipv4_address', 'placeholder' )
                terminal.set('port', 'placeholder')
            else:
                terminal.set('ipv4_address', ta['ip'] )
                terminal.set('port', ta['port'])

            # build node-b
            node = SubElement(nodes, 'node')
            node.set('id', 'b')
            cyclone_controller = SubElement(node, 'cyclone_controller')
            cyclone_controller.set('id', system_name + '-b')
            if input_info['deploy-type'] == 'HCI':
                hypervisor_host = SubElement(node, 'hypervisor_host')
                hypervisor_host.set('id', system_name + '-HOST-2')
            terminal = SubElement(node, 'terminal')
            if tb is False:
                terminal.set('ipv4_address', 'placeholder')
                terminal.set('port', 'placeholder')
            else:
                terminal.set('ipv4_address', tb['ip'])
                terminal.set('port', tb['port'])

        # build vcenters
        if 'vcenter' in input_info:
            for vc in input_info['vcenter'].split(','):
                vcenters = SubElement(root, 'vcenters')
                vcenter = SubElement(vcenters, 'vcenter')
                vcenter.set('id', vc)
                communication = SubElement(vcenter, 'communication')
                communication.set('ipv4_address', vc)
                communication.set('username', 'administrator@vsphere.local')
                communication.set('password', 'Password123!')
                management = SubElement(vcenter, 'management')
                management.set('username', 'administrator@vsphere.local')
                management.set('password', 'Password123!')

        # build trident hosts
        hosts = SubElement(root, 'hosts')
        for system_name in input_info['trident'].split(','):
            # node-a
            cyc_config_path = os.path.join(input_info['cyc-config-dir'], 'cyc-cfg.txt.' + system_name)
            config = get_cyc_config(cyc_config_path)
            host_a = SubElement(hosts, 'host')
            host_a.set('id', system_name + '-a')
            communication = SubElement(host_a, 'communication')
            communication.set('ipv4_address', config['local_ip_a'])
            communication.set('username', 'core')
            communication.set('password', 'cycpass')
            # node-b
            host_b = SubElement(hosts, 'host')
            host_b.set('id', system_name + '-b')
            communication = SubElement(host_b, 'communication')
            communication.set('ipv4_address', config['local_ip_b'])
            communication.set('username', 'core')
            communication.set('password', 'cycpass')
            if input_info['deploy-type'] == 'HCI':
                esx_1 = SubElement(hosts, 'host')
                esx_1.set('id', system_name + '-HOST-1')
                communication = SubElement(esx_1, 'communication')
                communication.set('ipv4_address', config['esx_ip_a'])
                communication.set('username', 'root')
                communication.set('password', 'Password123!')
                esx_2 = SubElement(hosts, 'host')
                esx_2.set('id', system_name + '-HOST-2')
                communication = SubElement(esx_2, 'communication')
                communication.set('ipv4_address', config['esx_ip_b'])
                communication.set('username', 'root')
                communication.set('password', 'Password123!')

        # build iSCSI IO hosts
        if 'iscsi-host' in input_info:
            for idx, host_ip in enumerate(input_info['iscsi-host'].split(','), 1):
                ihost = SubElement(hosts, 'host')
                ihost.set('id', 'iSCSI-IOVM-' + str(idx))
                communication = SubElement(ihost, 'communication')
                communication.set('ipv4_address', host_ip)
                communication.set('username', 'root')
                communication.set('password', 'Password123!')
                communication.set('role', 'io_host')

        # build FC IO hosts
        if 'fc-host' in input_info:
            for idx, host_ip in enumerate(input_info['fc-host'].split(','), 1):
                fchost = SubElement(hosts, 'host')
                fchost.set('id', 'FC-IOVM-' + str(idx))
                communication = SubElement(fchost, 'communication')
                communication.set('ipv4_address', host_ip)
                communication.set('username', 'cyc')
                communication.set('password', 'cycpass')
                communication.set('role', 'io_host')

        xmloutput = minidom.parseString(tostring(root)).toprettyxml(indent="  ")
        if 'output' in input_info:
            with open(input_info['output'], 'w+') as fh:
                fh.write(xmloutput)
            print("SUCC: testbed xml was wrote to {} ".format(input_info['output']))
        else:
            print(xmloutput)

