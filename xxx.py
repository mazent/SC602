# vedi http://ianharvey.github.io/bluepy-doc/index.html
from __future__ import print_function
from bluepy.btle import Peripheral

mac = '00:a0:50:9e:2b:a7'

dev = Peripheral(mac)

srvz = dev.getServices()
for srv in srvz:
    crt = srv.getCharacteristics()
    for c in crt:
        #uuid = str(c.uuid)
        uuid = c.uuid.getCommonName()
        pts = c.propertiesToString()
        print(uuid + ' : ' + pts)
        if c.supportsRead():
            r = c.read()
            print(str(r))

dev.disconnect()