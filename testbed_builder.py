#! python testbed_builder.py
import os,sys,re,getopt,subprocess
from xml.dom import minidom
from xml.etree.ElementTree import (
        Element, SubElement, Comment, tostring,
)
from pprint import pprint



class TestbedBuilder():

    def __init__(self, array=None, vcenter=None, cyc_configs_dir = '/opt/share/DevOpsCIT/configuration/devops-ctee-config/cyc_configs/', kwargs={}):

        self.build_info = kwargs
        self.build_info['array'] = array
        self.build_info['vcenter'] = vcenter
        self.build_info['cyc-config-dir'] = cyc_configs_dir

    def get_cyc_config(self, path):
        """ Read the cyc_config file from given path
        """
        configs= dict()
        if not os.path.exists(path):
            print("ERROR: Given cyc-config-path: %s doesn't exist!" % path)
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

    def terminal_info(self, array):
        """ get terminal info (IP and Port)
        """
        swarm = False
        try:
            res = subprocess.check_output(["swarm", array])
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

    def build(self):
        # starts to build
        if self.build_info['type'] == 'hci' and 'vcenter' not in self.build_info.keys(): 
            return ValueError("vcenter is required for HCI")
        root = Element('testbedinfo')
        root.set('version', '1.0')
        root.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
        root.set('xmlns:xsd', "http://www.w3.org/2001/XMLSchema")
        root.set('doc_type', "testbed")
        cyclones= SubElement(root, 'cyclones')
        if self.build_info['array'] == '':
            print('ERR: parameter "vcenter" is required when delopy-type is HCI!')
            exit(-1)
        else:
            for system_name in self.build_info['array'].split(','):
                cyc_config_path = os.path.join(self.build_info['cyc-config-dir'], 'cyc-cfg.txt.' + system_name)
                config = self.get_cyc_config(cyc_config_path)
                cyclone = SubElement(cyclones, 'cyclone')
                cyclone.set('name', system_name)
                if self.build_info['type'] == 'hci':
                    cyclone.set('datacenter_name', 'DataCenter' + system_name[2:] )
                    cyclone.set('name', 'Cluster' + system_name[2:] )
                    cyclone.set('vcenter', self.build_info['vcenter'])
                # build management_info
                management_info = SubElement(cyclone, 'management_info')
                management_info.set('management_ip_addr', config['cluster_ip'])
                # build appliances
                appliances = SubElement(cyclone, 'appliances')
                appliance = SubElement(appliances, 'appliance')
                appliance.set('id', system_name)
                appliance.set('ip_address', config['appliance_ip'])
                if 'cyc-config-path' in self.build_info:
                    appliance.set('cyc_config', self.build_info['cyc-config-path'])
                else: # default path
                    appliance.set('cyc_config', cyc_config_path)

                ta, tb = self.terminal_info(system_name)

                # build nodes
                nodes = SubElement(appliance, 'nodes')
                # build node-a
                node = SubElement(nodes, 'node')
                node.set('id', 'a')
                cyclone_controller = SubElement(node, 'cyclone_controller')
                cyclone_controller.set('id', system_name + '-a')
                if self.build_info['type'] == 'hci':
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
                if self.build_info['type'] == 'hci':
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
            if 'vcenter' in self.build_info.keys():
                for vc in self.build_info['vcenter'].split(','):
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

            # build array hosts
            hosts = SubElement(root, 'hosts')
            for system_name in self.build_info['array'].split(','):
                # node-a
                cyc_config_path = os.path.join(self.build_info['cyc-config-dir'], 'cyc-cfg.txt.' + system_name)
                config = self.get_cyc_config(cyc_config_path)
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
                if self.build_info['type'] == 'hci':
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
            if 'linux_host' in self.build_info.keys():
                for idx, host_ip in enumerate(self.build_info['linux_host'].split(','), 1):
                    ihost = SubElement(hosts, 'host')
                    ihost.set('id', 'iSCSI-Linux-IOVM-' + str(idx))
                    communication = SubElement(ihost, 'communication')
                    communication.set('ipv4_address', host_ip)
                    communication.set('username', 'root')
                    communication.set('password', 'Password123!')
                    communication.set('role', 'io_host')

            if 'windows_host' in self.build_info.keys():
                for idx, host_ip in enumerate(self.build_info['windows_host'].split(','), 1):
                    ihost = SubElement(hosts, 'host')
                    ihost.set('id', 'iSCSI-Windows-IOVM-' + str(idx))
                    communication = SubElement(ihost, 'communication')
                    communication.set('ipv4_address', host_ip)
                    communication.set('username', 'Administrator')
                    communication.set('password', 'Password123!')
                    communication.set('role', 'io_host')

            if 'esx_host' in self.build_info.keys():
                for idx, host_ip in enumerate(self.build_info['esx_host'].split(','), 1):
                    ihost = SubElement(hosts, 'host')
                    ihost.set('id', 'iSCSI-ESX-IOVM-' + str(idx))
                    communication = SubElement(ihost, 'communication')
                    communication.set('ipv4_address', host_ip)
                    communication.set('username', 'root')
                    communication.set('password', 'Password123!')
                    communication.set('role', 'io_host')

            # build FC IO hosts
            if 'fc_host' in self.build_info.keys():
                for idx, host_ip in enumerate(self.build_info['fc_host'].split(','), 1):
                    fchost = SubElement(hosts, 'host')
                    fchost.set('id', 'FC-IOVM-' + str(idx))
                    communication = SubElement(fchost, 'communication')
                    communication.set('ipv4_address', host_ip)
                    communication.set('username', 'cyc')
                    communication.set('password', 'cycpass')
                    communication.set('role', 'io_host')

            xmloutput = minidom.parseString(tostring(root)).toprettyxml(indent="  ")

            return(xmloutput)

