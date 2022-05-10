#coding=utf-8
#!/usr/bin/python

import os
import sys
import json
import argparse
from collections import OrderedDict

# Jumbo frame
JUMBO_MTU=9000

from onos import ONOSCluster, ONOSCLI
from bmv2 import ONOSBmv2Switch
from host6 import IPv6Host

from itertools import combinations
from time import sleep
from subprocess import call

from mininet.cli import CLI
from mininet.link import TCLink,Intf
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import RemoteController, Host
from mininet.topo import Topo


def getCmdBg(cmd, logfile="/dev/null"):
    return "{} > {} 2>&1 &".format(cmd, logfile)


class ClosTopo(Topo):

    def __init__(self, args, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)

        s01 = self.addSwitch("s01",
                             cls=ONOSBmv2Switch,
                             loglevel=args.log_level,
                             deviceId="1",
                             netcfg=True,
                             netcfgDelay=0.5,
                             pipeconf=args.pipeconf_id)

        s02 = self.addSwitch("s02",
		             cls=ONOSBmv2Switch,
		             loglevel=args.log_level,
		             deviceId="2",
		             netcfg=True,
		             netcfgDelay=0.5,
		             pipeconf=args.pipeconf_id)

        s03 = self.addSwitch("s03",
		             cls=ONOSBmv2Switch,
		             loglevel=args.log_level,
		             deviceId="3",
		             netcfg=True,
		             netcfgDelay=0.5,
		             pipeconf=args.pipeconf_id)

    	s04 = self.addSwitch("s04",
		             cls=ONOSBmv2Switch,
		             loglevel=args.log_level,
		             deviceId="4",
		             netcfg=True,
		             netcfgDelay=0.5,
		             pipeconf=args.pipeconf_id)

    	s05 = self.addSwitch("s05",
		             cls=ONOSBmv2Switch,
		             loglevel=args.log_level,
		             deviceId="5",
		             netcfg=True,
		             netcfgDelay=0.5,
		             pipeconf=args.pipeconf_id)

    	s06 = self.addSwitch("s06",
		             cls=ONOSBmv2Switch,
		             loglevel=args.log_level,
		             deviceId="6",
		             netcfg=True,
		             netcfgDelay=0.5,
		             pipeconf=args.pipeconf_id)

    	s07 = self.addSwitch("s07",
		             cls=ONOSBmv2Switch,
		             loglevel=args.log_level,
		             deviceId="7",
		             netcfg=True,
		             netcfgDelay=0.5,
		             pipeconf=args.pipeconf_id)

    	s08 = self.addSwitch("s08",
		             cls=ONOSBmv2Switch,
		             loglevel=args.log_level,
		             deviceId="8",
		             netcfg=True,
		             netcfgDelay=0.5,
		             pipeconf=args.pipeconf_id)

    	s09 = self.addSwitch("s09",
		             cls=ONOSBmv2Switch,
		             loglevel=args.log_level,
		             deviceId="9",
		             netcfg=True,
		             netcfgDelay=0.5,
		             pipeconf=args.pipeconf_id)

        self.addLink(s01, s02, cls=TCLink)
	self.addLink(s02, s03, cls=TCLink)
        self.addLink(s02, s04, cls=TCLink)
	self.addLink(s02, s09, cls=TCLink)
	self.addLink(s03, s05, cls=TCLink)
	self.addLink(s03, s06, cls=TCLink)
        self.addLink(s04, s05, cls=TCLink)
	self.addLink(s04, s06, cls=TCLink)
	self.addLink(s05, s07, cls=TCLink)
	self.addLink(s05, s08, cls=TCLink)
        self.addLink(s06, s07, cls=TCLink)
	self.addLink(s06, s08, cls=TCLink)
	self.addLink(s07, s09, cls=TCLink)
	self.addLink(s08, s09, cls=TCLink)
                               
        # 添加s1主机
        h11 = self.addHost('h11', cls=IPv6Host, mac="00:00:00:00:00:11", ipv4='10.1.1.1/24',
                           ipv6='2001:1:1::1/64', ipv6_gw='2001:1:1::ff', ipv4_gw='10.1.1.254')
        h12 = self.addHost('h12', cls=IPv6Host, mac="00:00:00:00:00:12", ipv4='10.1.1.2/24',
                           ipv6='2001:1:1::2/64', ipv6_gw='2001:1:1::ff', ipv4_gw='10.1.1.254')
        h13 = self.addHost('h13', cls=IPv6Host, mac="00:00:00:00:00:13", ipv4='10.1.1.3/24',
                           ipv6='2001:1:1::3/64', ipv6_gw='2001:1:1::ff', ipv4_gw='10.1.1.254')
        
        self.addLink(h11, s01,
                         cls=TCLink)  
        self.addLink(h12, s01,
                         cls=TCLink)  
	self.addLink(h13, s01,
                         cls=TCLink)  

        # 添加s15主机
        h51 = self.addHost('h51', cls=IPv6Host, mac="00:00:00:00:00:51", ipv4='10.1.5.1/24',
                          ipv6='2001:1:5::1/64', ipv6_gw='2001:1:5::ff', ipv4_gw='10.1.5.254')

        self.addLink(h51, s09,
                         cls=TCLink)   

def setMTU(net, mtu):
    for link in net.links:
        intf1 = link.intf1.name
        switchPort = intf1.split('-')
        sw1Name = switchPort[0]
        sw1 = net[sw1Name]

        intf2 = link.intf2.name
        switchPort = intf2.split('-')
        sw2Name = switchPort[0]
        sw2 = net[sw2Name]

        if isinstance(sw1, Host):
            continue

        if isinstance(sw2, Host):
            continue

        call(('ifconfig', intf1, 'mtu', str(mtu)))
        call(('ifconfig', intf2, 'mtu', str(mtu)))

def main(args):
    controller = RemoteController('c0', ip=args.onos_ip)
    onosIp = args.onos_ip
    topo = ClosTopo(args)
    net = Mininet(topo=topo, build=False, controller=[controller])
    net.build()
    collectorIntf = Intf('veth_1', node=net.nameToNode[ "s09" ] )
    net.start()
    print "Network started"
    setMTU(net, JUMBO_MTU)
    for h in net.hosts:
	h.startIperfServer()
    print "Iperf servers started"
    if not args.onos_ip:
        ONOSCLI(net)
    else:
        CLI(net)
    net.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='SRv6_INT Topo')
    parser.add_argument('--onos-ip', help='ONOS-BMv2 controller IP address',
                        type=str, action="store", required=False)
    parser.add_argument('--pipeconf-id', help='Pipeconf ID for switches',
                        type=str, action="store", required=False, default='')
    parser.add_argument('--log-level', help='BMv2 log level',
                        type=str, action="store", required=False, default='warn')
    setLogLevel('info')
    main(parser.parse_args())
