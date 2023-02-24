# -*- coding: utf-8 -*-
import upnpclient

# De
devices = upnpclient.discover()

print(devices)

d = devices[0]

ip = d.WANIPConn1.GetExternalIPAddress()['NewExternalIPAddress']
print(ip)
#status = d.WANIPConn1.actions
#print(status)
#d.WANIPConn1.DeletePortMapping(
#        NewRemoteHost='192.168.0.19',
#        NewExternalPort=3812,
#        NewProtocol='TCP')
#d.WANIPConn1.AddPortMapping(
#        NewRemoteHost='0.0.0.0',
#        NewExternalPort=3812,
#        NewProtocol='TCP',
#        NewInternalPort=3812,
#        NewInternalClient='192.168.0.19',
#        NewEnabled='1',
#        NewPortMappingDescription='Testing aze',
#        NewLeaseDuration=10000)
i = 0
while True:
    try:
        status = d.WANIPConn1.GetGenericPortMappingEntry(NewPortMappingIndex=i)
        i += 1
        print(status)
    except Exception as e:
        print(e)
        break
