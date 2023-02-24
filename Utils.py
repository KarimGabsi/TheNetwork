# -*- coding: utf-8 -*-
import socket, netifaces, os, sys
from uuid import uuid4
from enum import Enum
import json, time
from json import JSONEncoder
from datetime import datetime

from functools import wraps
import logging
import traceback

exceptionloggerfile = 'TheNetwork.log'
exceptionlogger = logging.getLogger('EXCEPTION_LOGGER')
exceptionlogger.setLevel(logging.DEBUG)
handler = logging.FileHandler(exceptionloggerfile)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s \t %(name)s \t %(levelname)s: \n%(message)s \n')
handler.setFormatter(formatter)
exceptionlogger.addHandler(handler)

# UUID4 CLASS
class UUID():
    def generateUUID(self):
        return str(uuid4())

# IP CONFIG CLASS
class IPConfig():
    def getlocalip(self):
        return socket.gethostbyname(socket.gethostname())
    
    def getexternalip(self):
        return os.popen('curl -s ifconfig.me').readline()
    
    def getdefaultgateway(self):
        gateways = netifaces.gateways()
        return gateways['default'][netifaces.AF_INET][0]

class TestConnection():
    def __init__(self, localip, externalip, port, timeout):
        self.localip = localip
        self.externalip = externalip
        self.port = port
        self.timeout = timeout
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.execute()
    
    def run_serv(self):
        try:
            self.serv.bind((self.localip, self.port))
            self.serv.listen()
        except:
            print('Cannot listen on: ', self.localip, self.port)
            self.isOnline = False
    
    def run_conn(self):
        self.conn.settimeout(self.timeout)
        result = self.conn.connect_ex((self.externalip, self.port))
        if result == 0:
            self.isOnline = True
        else:
            print('Cannot connect on: ', self.externalip, self.port)
            self.isOnline = False
    
    def execute(self):
        self.run_serv()
        self.run_conn()
        self.serv.close()
        self.conn.close()

# NETWORK UTILS
class NetworkState(Enum):
    LISTEN = 1
    AUTHENTICATION = 2
    HANDSHAKE = 3
    PINGPONG = 4
    MESSAGE = 5
    ADDRBOOK = 6
    READY = 7

class NetworkPeer():
    def __init__(self, ip, port, nodeid=None, lastping=None):
        self.ip = ip
        self.port = port
        
        if nodeid == None:
            self.nodeid = UUID().generateUUID()
        else:
            self.nodeid = nodeid
            
        if lastping == None:
            self.lastping = time.time()
        else:
            self.lastping = lastping

    def __eq__(self, other): 
        if not isinstance(other, NetworkPeer):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.nodeid == other.nodeid
    
    def toTuple(self):
        return (self.ip, self.port, self.nodeid, self.lastping)

# ENCODER
class MyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return dict(day=o.day, month=o.month, year=o.year, hour=o.hour, minute=o.minute, second=o.second)           
        else:
            return o.__dict__  

# MESSAGE
class Message():
    def __init__(self, message, ip, timestamp=None):
        self.message = message
        self.ip = ip
        if timestamp == None:
            self.timestamp = datetime.fromtimestamp(time.time())
        else:
            self.timestamp = timestamp
           
    def toJSON(self, networkstate):
        jsondata = {}
        jsondata['msgtype'] = '{}'.format(networkstate)
        jsondata['message'] = self.message
        jsondata['ip'] = self.ip
        jsondata['timestamp'] = self.timestamp
        return json.dumps(jsondata, default=MyEncoder().default)
    
    def __lt__(self, other):
        return self.timestamp < other.timestamp
    
#Custom Exception
class TNExceptionType(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3

class TNException(Exception):
    def __init__(self, message, TNExceptionType=TNExceptionType.INFO):
        super(TNException, self).__init__(message)
        self.TNExceptionType = TNExceptionType

#Wrapper
class Wrapper(object):
    @staticmethod
    def Clear_Log():
        with open(exceptionloggerfile, 'w'):
            pass
            
    @staticmethod
    def Class_Handler(decorator):
        def class_wrapper(cls):
            for attr in cls.__dict__:
                func = getattr(cls, attr)
                if callable(func):
                    setattr(cls, attr, decorator(func))
            return cls
        return class_wrapper
    
    @staticmethod
    def Exception_Handler(func):
        @wraps(func)
        def exception_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TNException as tne:
                trace = ''.join(traceback.format_exception(etype=type(tne), value=tne, tb=tne.__traceback__))
                if tne.TNExceptionType == TNExceptionType.INFO:
                    eMessage = Wrapper.Compose_eMessage(type(tne).__name__, tne, func.__code__, func.__name__)
                    exceptionlogger.info(eMessage)
                    print(eMessage)
                elif tne.TNExceptionType == TNExceptionType.WARNING:
                    eMessage = Wrapper.Compose_eMessage(type(tne).__name__, tne, func.__code__, func.__name__, trace)
                    exceptionlogger.warning(eMessage)
                    print(eMessage)
                elif tne.TNExceptionType == TNExceptionType.ERROR:
                    eMessage = Wrapper.Compose_eMessage(type(tne).__name__, tne, func.__code__, func.__name__, trace)
                    exceptionlogger.error(eMessage)
                    print(eMessage)
                    sys.exit(1)
            except Exception as e:
                trace = ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
                eMessage = Wrapper.Compose_eMessage(type(e).__name__, e, func.__code__, func.__name__, trace)
                exceptionlogger.critical(eMessage)
                print(eMessage)
                sys.exit(1)
        return exception_wrapper
   
    @staticmethod
    def Compose_eMessage(ename, emessage, funccode, funcname, trace=''):
        return 'Exception [{0}]: {1}\n{2} \n-->{3}(...)\n{4}'.format(ename, emessage, funccode, funcname, trace)