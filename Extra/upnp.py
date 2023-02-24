# -*- coding: utf-8 -*-

import socket
get_local_ip = lambda: socket.gethostbyname(socket.gethostname())

class upnp():
    def __init__(self):
        self.hostname = None
        self.port = None
        self.locationurl = None
        self.path = None
        
        self.processResponse(self.requestToRouter())
        
    def requestToRouter(self):
        SSDP_ADDR = "239.255.255.250"
        SSDP_PORT = 1900
        SSDP_MX = 2
        SSDP_ST = "urn:schemas-upnp-org:device:InternetGatewayDevice:1"
        
        ssdpRequest = "M-SEARCH * HTTP/1.1\r\n" + \
                        "HOST: %s:%d\r\n" % (SSDP_ADDR, SSDP_PORT) + \
                        "MAN: \"ssdp:discover\"\r\n" + \
                        "MX: %d\r\n" % (SSDP_MX, ) + \
                        "ST: %s\r\n" % (SSDP_ST, ) + "\r\n"
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(ssdpRequest, 'utf-8'), (SSDP_ADDR, SSDP_PORT))
        response = str(sock.recv(1000), 'utf-8')
        print(response)
        return response
    
    def processResponse(self, response):
        data = response.split('\r\n')   
        location = [x for x in data if x.lower().startswith('location:')]
        self.locationurl = location[0].lower().replace('location: ', '')

        from urllib.parse import urlparse
        myparse = urlparse(self.locationurl)
        self.hostname = myparse.hostname
        self.port = myparse.port
        
        from urllib.request import urlopen
        directory = urlopen(self.locationurl).read()

        from xml.dom.minidom import parseString
        dom = parseString(directory)
        
        service_types = dom.getElementsByTagName('serviceType')
        for service in service_types:
            if service.childNodes[0].data.find('WANIPConnection') > 0:
                self.path = service.parentNode.getElementsByTagName('controlURL')[0].childNodes[0].data
    
    def createTCPPortDocument(self, ip, port, description):
        from xml.dom.minidom import Document
        
        doc = Document() 
        
        # create the envelope element and set its attributes
        envelope = doc.createElementNS('', 's:Envelope')
        envelope.setAttribute('xmlns:s', 'http://schemas.xmlsoap.org/soap/envelope/')
        envelope.setAttribute('s:encodingStyle', 'http://schemas.xmlsoap.org/soap/encoding/')
        
        # create the body element
        body = doc.createElementNS('', 's:Body')
        
        # create the function element and set its attribute
        fn = doc.createElementNS('', 'u:AddPortMapping')
        fn.setAttribute('xmlns:u', 'urn:schemas-upnp-org:service:WANIPConnection:1')
        
        # setup the argument element names and values
        # using a list of tuples to preserve order
        arguments = [
            ('NewExternalPort', '{0}'.format(port)),           # specify port on router
            ('NewProtocol', 'TCP'),                            # specify protocol
            ('NewInternalPort', '{0}'.format(port)),           # specify port on internal host
            ('NewInternalClient', '{0}'.format(ip)),           # specify IP of internal host
            ('NewEnabled', '1'),                               # turn mapping ON
            ('NewPortMappingDescription', '{0}'.format(description)), # add a description
            ('NewLeaseDuration', '0')]                         # how long should it be opened?
        
        # NewEnabled should be 1 by default, but better supply it.
        # NewPortMappingDescription Can be anything you want, even an empty string.
        # NewLeaseDuration can be any integer BUT some UPnP devices don't support it,
        # so set it to 0 for better compatibility.
        
        # container for created nodes
        argument_list = []
        
        # iterate over arguments, create nodes, create text nodes,
        # append text nodes to nodes, and finally add the ready product
        # to argument_list
        for k, v in arguments:
            tmp_node = doc.createElement(k)
            tmp_text_node = doc.createTextNode(v)
            tmp_node.appendChild(tmp_text_node)
            argument_list.append(tmp_node)
        
        # append the prepared argument nodes to the function element
        for arg in argument_list:
            fn.appendChild(arg)
        
        # append function element to the body element
        body.appendChild(fn)
        
        # append body element to envelope element
        envelope.appendChild(body)
        
        # append envelope element to document, making it the root element
        doc.appendChild(envelope)
        
        # our tree is ready, conver it to a string
        return doc.toxml()
    
    def postToRouter(self, xml):
        import http.client
        # use the object returned by urlparse.urlparse to get the hostname and port
        conn = http.client.HTTPConnection(self.hostname, self.port)
        
        # use the path of WANIPConnection (or WANPPPConnection) to target that service,
        # insert the xml payload,
        # add two headers to make tell the server what we're sending exactly.
        conn.request('POST',
            self.path,
            xml,
            {'SOAPAction': '"urn:schemas-upnp-org:service:WANIPConnection:1#AddPortMapping"',
             'Content-Type': 'text/xml'}
        )
        
        # wait for a response
        resp = conn.getresponse()
        
        # print the response status
        print(resp.status)
        
        # print the response body
        print (resp.read())
    def returnInfo(self):
        return 'hostname:{0}\nport:{1}\nlocationurl:{2}\npath:{3}\n'.format(self.hostname, self.port, self.locationurl, self.path)

if __name__ == '__main__':
    myUPNP = upnp()
    print(myUPNP.returnInfo())
    
    tcpDoc = myUPNP.createTCPPortDocument(get_local_ip(), 5999, 'Opening Port Test Description')
    
    myUPNP.postToRouter(tcpDoc)
    