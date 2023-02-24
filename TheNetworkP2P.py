# -*- coding: utf-8 -*-
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver
from twisted.protocols.policies import TimeoutMixin
import json, time

from Utils import NetworkState, NetworkPeer, Message, Wrapper, IPConfig, TNException, TNExceptionType
from Encryption import Encryption

#PING_INTERVAL = 1200.0 # 20 min = 1200.0
PING_INTERVAL = 10 # 10 seconds

@Wrapper.Class_Handler(Wrapper.Exception_Handler)
class TheNetworkProtocol(LineReceiver, TimeoutMixin):
    LineReceiver.delimiter = b'\r\n'
    def __init__(self, factory, tncpoint=None):  
        self.factory = factory
        self.setTimeout(10)
        self.isConnected = False
        self.encryption = Encryption(self.factory.p2p_cluster.key)
        self.state = NetworkState.LISTEN
        self.lc_ping = LoopingCall(self.send_ping)
        self.lc_managep2pqueue = LoopingCall(self.manageP2PQueue).start(0)
        self.remotepeer = None
        self.tncPoint = tncpoint
        self.authenticated = False

    def connectionMade(self):
        self.isConnected = True
        if self.transport.getPeer().host != IPConfig().getdefaultgateway():
            print('Connection made with ', self.transport.getPeer().host, self.transport.getPeer().port)
            print('From ', self.transport.getHost().host, self.transport.getHost().port)
            
            self.send_handshake()
        else:
            print('Default Gateway connection made...')

    def connectionLost(self, reason): 
        print('CONNECTION LOST')
        if not self.remotepeer == None:
            if self.remotepeer in self.factory.peers:
                self.factory.peers.remove(self.remotepeer)
            print ('Disconnecting: ', self.transport.getPeer(), self.remotepeer.nodeid)
            self.lc_ping.stop()
        
    def timeoutConnection(self):
        if not self.isConnected:
            print('OFFLINE | TIMEOUT: ', self.tncPoint._host, self.tncPoint._port)
            self = None #Delete current instance of connection.
        else:
            print('Connected and fake timed out')   
            
    def lineReceived(self, data):
        try:
            data = self.encryption.Decrypt(data)
            jsondata = json.loads(data)
            if jsondata['msgtype'] == '{0}'.format(NetworkState.HANDSHAKE):
                self.state = NetworkState.HANDSHAKE
                self.handle_handshake(data)
                self.state = NetworkState.READY
            elif jsondata['msgtype'] == '{0}'.format(NetworkState.PINGPONG):
                self.state = NetworkState.PINGPONG
                self.handle_pingpong(data)
                self.state = NetworkState.READY
            elif jsondata['msgtype'] == '{0}'.format(NetworkState.ADDRBOOK):
                self.state = NetworkState.ADDRBOOK
                self.handle_addrbook(data)
                self.state = NetworkState.READY
            elif jsondata['msgtype'] == '{0}'.format(NetworkState.MESSAGE):
                self.state = NetworkState.MESSAGE
                self.handle_message(data)
                self.state = NetworkState.READY
        except:
            #lose connection
            self.transport.loseConnection()
            message = 'ERROR ENCRYPT/DECTYPT | NOT AUTHORIZED | {0}:{1} <-> {2}:{3}'.format(
                    self.transport.getPeer().host,
                    self.transport.getPeer().port,
                    self.transport.getHost().host,
                    self.transport.getHost().port)
            raise TNException(message, TNExceptionType.WARNING)
            
    def int_to_bytes(self, x):
        return x.to_bytes((x.bit_length() + 7) // 8, 'big')
    def findByNodeId(self, peers, nodeid):
        for peer in peers:
            if peer.nodeid == nodeid:
                return peer
        return None
    
    def manageP2PQueue(self):
        if not self.factory.p2p_queue.empty():
            item = self.factory.p2p_queue.get()
            function = item[0]
            args = item[1:]
            #print('function: ', function, 'args: ', args)
            if function.lower() == 'send_message':
                self.send_message(args[0])
    
    def send_message(self, message):
        self.transport_write(message.toJSON(NetworkState.MESSAGE))
        
    def handle_message(self, data):
        jsondata = json.loads(data)
        message = Message(jsondata['message'],jsondata['ip'], jsondata['timestamp'])
        self.factory.gui_queue.put(('receive_message', message))
    
    def send_handshake(self):        
        jsondata = {}
        jsondata['msgtype'] = '{0}'.format(NetworkState.HANDSHAKE)
        jsondata['peer'] = self.factory.mypeer.toTuple()
        self.transport_write(json.dumps(jsondata))
            
    def handle_handshake(self, data):
        jsondata = json.loads(data)
        recvpeer = jsondata["peer"]
        self.remotepeer = NetworkPeer(recvpeer[0],recvpeer[1],recvpeer[2])
        if self.remotepeer.nodeid == self.factory.mypeer.nodeid:
            print ("Connected to myself.")
            #self.transport.loseConnection()
        else:
            print ("Connected with nodeid: ", self.remote_nodeid)    
        
        p = self.findByNodeId(self.factory.peers, self.remotepeer.nodeid)
        p.lastping = time.time()
        self.lc_ping.start(PING_INTERVAL)
        self.send_addrbook(mine=True)
        self.send_addrbook()
                  
    def send_ping(self):
        jsondata = {}
        jsondata['msgtype'] = '{0}'.format(NetworkState.PINGPONG)
        jsondata['message'] = 'PING'
        self.transport_write(json.dumps(jsondata))
            
    def send_pong(self):
        jsondata = {}
        jsondata['msgtype'] = '{0}'.format(NetworkState.PINGPONG)
        jsondata['message'] = 'PONG'
        self.transport_write(json.dumps(jsondata))
    
    def handle_pingpong(self, data):
        jsondata = json.loads(data)
        message = jsondata['message']
        if message == 'PING':
            print('Sending PING from', self.factory.mypeer.nodeid)
            self.send_pong()
        elif message == 'PONG':
            p = self.findByNodeId(self.factory.peers, self.remotepeer.nodeid)
            p.lastping = time.time()
            print('Received PONG from', self.remotepeer.nodeid)
            print('PEERS: ', [(peer.ip, peer.port, peer.nodeid, peer.lastping) for peer in self.factory.peers])
            
    def send_addrbook(self, mine=False):
        now = time.time()
        if mine:
            peers = [self.factory.mypeer.toTuple()]
        else:
            peers = [peer.toTuple() for peer in self.factory.peers if peer.lastping > now-120]
            
        jsondata = {}
        jsondata['msgtype'] = '{0}'.format(NetworkState.ADDRBOOK)
        jsondata['peers'] = peers
        self.transport_write(json.dumps(jsondata))
        
    def handle_addrbook(self, data):
        jsondata = json.loads(data)
        peers = []
        for recvpeer in jsondata["peers"]:
            peers.append(NetworkPeer(recvpeer[0], recvpeer[1], recvpeer[2]))
            
        for peer in peers:
            if peer not in self.factory.peers:
                #Add peer to list
                self.factory.peers.append(peer)
                #Connect to peer
                tncPoint = TCP4ClientEndpoint(reactor, peer.ip, peer.port)
                connectProtocol(tncPoint, TheNetworkProtocol(self.factory, tncPoint))
        
        clusterpeers = []
        for peer in self.factory.peers:
            clusterpeers.append((peer.ip, peer.port))
        
        self.factory.p2p_cluster.append_cluster_file(clusterpeers)
        
    def transport_write(self, data):
        encrypted = self.encryption.Encrypt(data)
        self.transport.write(('{0}\r\n'.format(encrypted.decode())).encode())

@Wrapper.Class_Handler(Wrapper.Exception_Handler)
class TheNetworkFactory(Factory):
#    @Wrapper.Exception_Handler
    def __init__(self, externalip, port, gui_queue, p2p_queue, p2p_cluster):
        self.mypeer = NetworkPeer(externalip, port)
        self.peers = [self.mypeer]
        self.gui_queue = gui_queue
        self.p2p_queue = p2p_queue
        self.p2p_cluster = p2p_cluster
           
    def buildProtocol(self, addr):
        return TheNetworkProtocol(self)

@Wrapper.Class_Handler(Wrapper.Exception_Handler)
class TheNetworkP2P():
    def __init__(self, localip, port, externalip, gui_queue, p2p_queue, p2p_cluster):
        self.localhost = localip
        self.factory = TheNetworkFactory(externalip, port, gui_queue, p2p_queue, p2p_cluster)
        self.lc_connect = LoopingCall(self.connectall)
        self.start()            
        
    def start(self):
        if not reactor.running:
            print('The Network P2P Starting.')
            self.listen()
            self.lc_connect.start(1, now=False) #Connect to self in 1 second.
            reactor.run()
    
    def stop(self):
        if reactor.running:
            reactor.stop()
            print('The Network P2P Stopped.')
            
    def listen(self):
        print('Listening from {0}:{1}'.format(self.localhost, self.factory.mypeer.port))
        TheNetworkEndpoint = TCP4ServerEndpoint(reactor, self.factory.mypeer.port, interface=self.localhost)
        TheNetworkEndpoint.listen(self.factory)
            
    def connect(self, ip , port):
        print('Connecting to {0}:{1}'.format(ip, port))
        tncPoint = TCP4ClientEndpoint(reactor, ip, port)
        connectProtocol(tncPoint, TheNetworkProtocol(self.factory, tncPoint))

    def connectall(self):   
        self.lc_connect.stop()

        #Connect to self
        self.connect(self.factory.mypeer.ip, self.factory.mypeer.port)
        
        #Connect to cluster peers
        for ip, port in self.factory.p2p_cluster.peers:
            #Prevent connection to self...
            if ip != self.factory.mypeer.ip and port != self.factory.mypeer.port:
                self.connect(ip, port)