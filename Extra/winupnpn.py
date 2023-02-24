# -*- coding: utf-8 -*-
import upnp
device = upnp.Objects.Device()
device.deviceType = 'urn:sadmin-fr:device:demo:1'
device.friendlyName = 'UPnP Test'
device.uuid = '00a56575-78fa-40fe-b107-8f4b5043a2b0'
device.manufacturer = 'BONNET'
device.manufacturerURL = 'http://sadmin.fr'

service = upnp.Service()
service.serviceType = 'sadmin-fr:service:dummy'
service.serviceId = 'sadmin-fr:serviceId:1'

device.addService(service)
server = upnp.Annoncer(device)
server.initLoop()
server.notify()
server.foreaver()
server.dispose()