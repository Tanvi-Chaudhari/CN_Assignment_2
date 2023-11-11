#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class CustomRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(CustomRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def printRoutingTable(self):
        print(self.cmd('route'))

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(CustomRouter, self).terminate()

class CustomTopology(Topo):
    "A CustomRouter connecting three IP subnets"

    def build(self, **_opts):
        defaultIP = '192.168.1.1/24'
        custom_r1 = self.addNode('custom_r1', cls=CustomRouter, ip=defaultIP)
        custom_r2 = self.addNode('custom_r2', cls=CustomRouter, ip='172.16.0.1/12')
        custom_r3 = self.addNode('custom_r3', cls=CustomRouter, ip='10.0.0.1/8')

        s1, s2, s3 = [self.addSwitch(s) for s in ('s1', 's2', 's3')]

        self.addLink(s1, custom_r1, intfName2='custom_r1-eth1', params2={'ip': defaultIP})
        self.addLink(s2, custom_r2, intfName2='custom_r2-eth1', params2={'ip': '172.16.0.1/12'})
        self.addLink(s3, custom_r3, intfName2='custom_r3-eth1', params2={'ip': '10.0.0.1/8'})

        h1 = self.addHost('h1', ip='192.168.1.100/24', defaultRoute='via 192.168.1.1')
        h2 = self.addHost('h2', ip='192.168.1.101/24', defaultRoute='via 192.168.1.1')
        h3 = self.addHost('h3', ip='172.16.0.100/12', defaultRoute='via 172.16.0.1')
        h4 = self.addHost('h4', ip='172.16.0.101/12', defaultRoute='via 172.16.0.1')
        h5 = self.addHost('h5', ip='10.0.0.100/8', defaultRoute='via 10.0.0.1')
        h6 = self.addHost('h6', ip='10.0.0.101/8', defaultRoute='via 10.0.0.1')

        for h, s in [(h1, s1), (h2, s1), (h3, s2), (h4, s2), (h5, s3), (h6, s3)]:
            self.addLink(h, s)

        # Add router-router link in a new subnet for the router-router connection
        self.addLink(custom_r1, custom_r2, intfName1='custom_r1-eth2', intfName2='custom_r2-eth2', params1={'ip': '10.100.0.1/24'}, params2={'ip': '10.100.0.2/24'})
        self.addLink(custom_r2, custom_r3, intfName1='custom_r2-eth3', intfName2='custom_r3-eth2', params1={'ip': '10.101.0.1/24'}, params2={'ip': '10.101.0.2/24'})
        self.addLink(custom_r3, custom_r1, intfName1='custom_r3-eth3', intfName2='custom_r1-eth3', params1={'ip': '10.102.0.1/24'}, params2={'ip': '10.102.0.2/24'})

def run():
    "Test Custom router"
    topo = CustomTopology()
    net = Mininet(topo=topo, waitConnected=True)
    net.start()
    info('* Routing Table on Router custom_r1:\n')
    net['custom_r1'].printRoutingTable()
    info('* Routing Table on Router custom_r2:\n')
    net['custom_r2'].printRoutingTable()
    info('* Routing Table on Router custom_r3:\n')
    net['custom_r3'].printRoutingTable()

    # Add static routes for subnets not directly connected
    net['custom_r1'].cmd('ip route add 172.16.0.0/12 via 10.100.0.2')
    net['custom_r1'].cmd('ip route add 10.0.0.0/8 via 10.102.0.1')

    net['custom_r2'].cmd('ip route add 192.168.1.0/24 via 10.100.0.1')
    net['custom_r2'].cmd('ip route add 10.0.0.0/8 via 10.101.0.2')

    net['custom_r3'].cmd('ip route add 192.168.1.0/24 via 10.102.0.2')
    net['custom_r3'].cmd('ip route add 172.16.0.0/12 via 10.101.0.1')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
