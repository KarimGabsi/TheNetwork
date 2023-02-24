import hashlib, os
from Utils import Wrapper, TNException, TNExceptionType

@Wrapper.Class_Handler(Wrapper.Exception_Handler)
class Cluster():
    #path = Cluster/x.tnc
    #key = sha512 hash
    #peers = [(ip, port), (ip, port), ...]
    def __init__(self, path):
        fname, fext = os.path.splitext(path)
        self.path = path
        self.key = None
        self.peers = []
        self.read_cluster_file()
        if fext != '.tnc':
            raise TNException('Wrong file format', TNExceptionType.WARNING)
           
    def analyze_cluster_file(self, data):
        datalen = len(data)
        if datalen >= 64 and (datalen-64) % 6 == 0:
            keybytes = [self.bytes_to_int(x) for x in data[0:64]]
            self.key = ''.join('{:02x}'.format(x) for x in keybytes)
            i = 64
            self.peers = []
            while (i+6) <= len(data):
                self.peers.append(self.translate_peer(data[i:i+6]))
                i += 6
        else:
            raise TNException('Incompatible file', TNExceptionType.ERROR)
    
    def translate_peer(self, data):
        if len(data) == 6:
            ip = '{0}.{1}.{2}.{3}'.format(
                    self.bytes_to_int(data[0]),
                    self.bytes_to_int(data[1]),
                    self.bytes_to_int(data[2]),
                    self.bytes_to_int(data[3]),)
            
            port = self.bytes_to_int(data[4] + data[5])
            return (ip, port)
        else:
            raise TNException('Peer tranlation failure', TNExceptionType.ERROR)
    
    def password_to_key(self, password):
        return hashlib.sha512(password.encode('utf-8')).hexdigest()
        
    def compose_cluster_file(self, key, peers):
        data = []
        #key
        keyint = int('0x{}'.format(key), 0)
        keybytes = self.int_to_bytes(keyint)
        for keypart in list(keybytes):
            data.append(self.int_to_bytes(keypart))
        
        #peer
        for peer in peers:
            ip = peer[0]
            port = peer[1]
            peerbytes = self.compose_peers(ip, port)
            for peerb in peerbytes:
                data.append(peerb)
        
        return data
    
    def compose_peers(self, ip, port):
        data = []
        addr = [int(x) for x in ip.split('.')]
        
        for ip_part in addr:
            if ip_part >= 0 and ip_part <= 255:
                data.append(self.int_to_bytes(ip_part))
            else:
                raise TNException('Part of ip is not of correct byte-size', TNExceptionType.ERROR)
            
        if port >= 0 and port <= 65535:
            for pp in list(self.int_to_bytes(port)):
                data.append(self.int_to_bytes(pp))
        else:
            raise TNException('Port is not of correct byte-size', TNExceptionType.ERROR)
        
        return data
    
    def int_to_bytes(self, x):
        return x.to_bytes((x.bit_length() + 7) // 8, 'big')
    
    def bytes_to_int(self, xbytes):
        return int.from_bytes(xbytes, 'big')

    def read_cluster_file(self):
        data = []
        with open(self.path, 'rb') as f:
            byte = f.read(1)
            while byte != b"":
                data.append(byte)
                byte = f.read(1)
        self.analyze_cluster_file(data)
         
    def create_cluster_file(self, password, peers):
        key = self.password_to_key(password)
        data = self.compose_cluster_file(key, peers)
        self.write_cluster_file(data)
                    
    def append_cluster_file(self, peers):
        if not self.key:
            raise TNException('No key for file, create file first!', TNExceptionType.ERROR)
            
        for ip, port in peers:
            if not (ip, port) in self.peers:
                self.peers.append((ip, port))
        
        data = self.compose_cluster_file(self.key, self.peers)
        self.write_cluster_file(data)
    
    def write_cluster_file(self, data):
        with open(self.path, 'wb') as f:
            for b in data:
                if b == b"":
                    f.write(b'\x00')
                else:
                    f.write(b)
                    
        self.read_cluster_file()
            

#path = 'Cluster/global.tnc'
#password = 'B4Z1NG4'
##peers = [('127.0.0.1', 1234), ('178.118.85.77', 4319), ('188.113.49.12', 5555)]
#peers = [('127.0.0.1', 1234), ('178.118.85.77', 4319), ('188.113.49.12', 5555), ('192.168.0.19', 4319)]
#peers = [('178.118.85.77', 4319)]
#cluster = Cluster(path)
#cluster.create_cluster_file(password, peers)
##newpeers = [('127.0.0.1', 1235)]
##cluster.append_cluster_file(newpeers)
#print(cluster.key)
#print(cluster.peers)
