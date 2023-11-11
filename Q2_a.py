from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class CustomHost(Node):
    "Custom host class."

    def config(self, **params):
        super(CustomHost, self).config(**params)

class CustomTopology(Topo):
    "My custom topology."

    def build(self):
        "Build custom topology."

        # Add hosts and switches with new variable names
        MyHost1 = self.addHost('h1')
        MyHost2 = self.addHost('h2')
        MyHost3 = self.addHost('h3')
        MyHost4 = self.addHost('h4')
        MySwitch1 = self.addSwitch('s1')
        MySwitch2 = self.addSwitch('s2')

        # Add links with new variable names
        self.addLink(MyHost1, MySwitch1)
        self.addLink(MyHost2, MySwitch1)
        self.addLink(MyHost3, MySwitch2)
        self.addLink(MyHost4, MySwitch2)
        self.addLink(MySwitch1, MySwitch2)

topos = {'customtopo': (lambda: CustomTopology())}

def run():
    "Run custom topology"
    topo = CustomTopology()
    net = Mininet(topo=topo, waitConnected=True)
    net.start()
    
    # Add any custom configurations or commands here
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
