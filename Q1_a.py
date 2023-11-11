from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class CustomRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(CustomRouter, self).config(**params)
        # Enable forwarding on the router
        self.cmd('sysctl net.ipv4.ip_forward=1')
        # Configure the routing table
        self.cmd('ip route add default via 192.168.2.2 dev x')
        self.cmd('ip route add 192.168.1.0/24 dev custom-eth1')
        self.cmd('ip route add 10.0.0.0/24 via 192.168.2.2 dev x')
        self.cmd('ip route add 172.16.0.0/24 via 172.16.2.2 dev u')

    def printRoutingTable(self):
        print(self.cmd('route'))

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(CustomRouter, self).terminate()

class CustomTopology(Topo):
    "A CustomRouter connecting three IP subnets"

    def build(self, **_opts):
        # Subnet 1
        subnet1 = '192.168.1.0/24'
        custom_ra = self.addNode('custom_ra', cls=CustomRouter, ip='192.168.1.1/24')
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1', ip='192.168.1.100/24', defaultRoute='via 192.168.1.1')
        h2 = self.addHost('h2', ip='192.168.1.101/24', defaultRoute='via 192.168.1.1')

        # Subnet 2
        subnet2 = '10.0.0.0/24'
        custom_rb = self.addNode('custom_rb', cls=CustomRouter, ip='10.0.0.1/24')
        s2 = self.addSwitch('s2')
        h3 = self.addHost('h3', ip='10.0.0.100/24', defaultRoute='via 10.0.0.1')
        h4 = self.addHost('h4', ip='10.0.0.101/24', defaultRoute='via 10.0.0.1')

        # Subnet 3
        subnet3 = '172.16.0.0/24'
        custom_rc = self.addNode('custom_rc', cls=CustomRouter, ip='172.16.0.1/24')
        s3 = self.addSwitch('s3')
        h5 = self.addHost('h5', ip='172.16.0.100/24', defaultRoute='via 172.16.0.1')
        h6 = self.addHost('h6', ip='172.16.0.101/24', defaultRoute='via 172.16.0.1')

        # Connect subnets to routers
        self.addLink(s1, custom_ra, intfName2='custom-eth1', params2={'ip': '192.168.1.1/24'})
        self.addLink(s2, custom_rb, intfName2='custom-eth1', params2={'ip': '10.0.0.1/24'})
        self.addLink(s3, custom_rc, intfName2='custom-eth1', params2={'ip': '172.16.0.1/24'})
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        self.addLink(h5, s3)
        self.addLink(h6, s3)

        # Add links between routers
        self.addLink(custom_ra, custom_rb, intfName1='x', intfName2='y', params1={'ip': '192.168.2.1/24'}, params2={'ip': '192.168.2.2/24'})
        self.addLink(custom_rb, custom_rc, intfName1='t', intfName2='v', params1={'ip': '10.0.2.1/24'}, params2={'ip': '10.0.2.2/24'})
        self.addLink(custom_ra, custom_rc, intfName1='u', intfName2='w', params1={'ip': '172.16.2.1/24'}, params2={'ip': '172.16.2.2/24'})
        
        # Additional links between routers to correct connectivity
        self.addLink(custom_ra, custom_rb, intfName1='z', intfName2='t', params1={'ip': '10.0.1.1/24'}, params2={'ip': '10.0.1.2/24'})
        self.addLink(custom_rb, custom_rc, intfName1='s', intfName2='u', params1={'ip': '172.16.1.1/24'}, params2={'ip': '172.16.1.2/24'})
        self.addLink(custom_ra, custom_rc, intfName1='v', intfName2='z', params1={'ip': '192.168.3.1/24'}, params2={'ip': '192.168.3.2/24'})

    def printRoutingTables(self, net):
        for router_name in ['custom_ra', 'custom_rb', 'custom_rc']:
            router = net[router_name]
            print(f"Routing table for {router_name}:")
            router.printRoutingTable()
            print()

topos = {'customtopo': (lambda: CustomTopology())}

def run():
    "Test Custom router"
    topo = CustomTopology()
    net = Mininet(topo=topo, waitConnected=True)
    net.start()

    # Print routing tables for all routers
    topo.printRoutingTables(net)

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
