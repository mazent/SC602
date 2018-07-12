# vedi http://ianharvey.github.io/bluepy-doc/index.html
from __future__ import print_function
from bluepy.btle import Peripheral, DefaultDelegate
import json
import time
import uuid
import struct

mac = '00:a0:50:9e:2b:a7'

class delega(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print(data)


crtS = None
crtL = None

dev = Peripheral(mac)
dev.setMTU(1000)

dlg = delega()
dev.withDelegate(dlg)

srvz = dev.getServices()
for srv in srvz:
    crt = srv.getCharacteristics()
    for c in crt:
        cuuid = c.uuid.getCommonName()
        pts = c.propertiesToString()
        print(cuuid + ' : ' + pts)
        # if c.supportsRead():
        #     r = c.read()
        #     print(str(r))
        if str(c.uuid) == cuuid:
            if c.supportsRead():
                crtL = c # c.getHandle()
            else:
                crtS = c # c.getHandle()

if crtL is not None:
    x = crtL.read()
    l = struct.unpack('<B', x)
    print('letto %d' % l[0])

    x = crtL.read()
    l = struct.unpack('<B', x)
    print('letto %d' % l[0])

if crtS is not None:
    #cmd_ver = {'TS': int(time.time()), 'MSG': str(uuid.uuid4())}
    cmd_ver = {'TS': int(time.time())}

    c = json.JSONEncoder().encode(cmd_ver)

    print('versione')
    #dev.writeCharacteristic(crtS, c, True)
    #c = c.replace(' ', '')
    crtS.write(c.encode('ascii'), True)

    if dev.waitForNotifications(2.0):
        print('ok')
    else:
        print('err')

dev.disconnect()
