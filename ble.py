#! /usr/bin/env python

from __future__ import print_function

from bluepy.btle import Peripheral, DefaultDelegate
import json
import time
import random
import string

try:
    # 2
    import Queue as coda
except ImportError:
    # 3
    import queue as coda


class _delega(DefaultDelegate):
    def __init__(self, coda):
        DefaultDelegate.__init__(self)
        self.coda = coda

    def handleNotification(self, cHandle, data):
        self.coda.put((cHandle, data))

def _acaso(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class BLE(object)

    def __init__(self, mac):
        self.coda = coda.Queue()

        dlg = _delega(, self.coda)
        try:
            self.dev = Peripheral(mac)
            self.dev.setMTU(512)
            self.dev.withDelegate(dlg)

            self.crtL = None
            self.crtS = None

            srvz = dev.getServices()
            for srv in srvz:
                crt = srv.getCharacteristics()
                for c in crt:
                    cuuid = c.uuid.getCommonName()
                    pts = c.propertiesToString()
                    print(cuuid + ' : ' + pts)
                    if str(c.uuid) == cuuid:
                        if c.supportsRead():
                            self.crtL = c
                        else:
                            self.crtS = c
        except bluepy.btle.BTLEException:
            self.dev = None

    def __del__(self):
        if self.dev is not None:
            self.dev.disconnect()

    def a_posto(self):
        return self.crtS is not None

    def versione(self, dim=0):
        cmd_ver = {'TS': int(time.time())}
        cmd = json.JSONEncoder().encode(cmd_ver)

        # Aggiungo "X": "..."
        if dim > len(cmd) + 3 + 2 + 2 :
            cmd_ver['X'] = _acaso(len(cmd) - (3 + 2 + 2))
            cmd = json.JSONEncoder().encode(cmd_ver)

        self.crtS.write(cmd, True)

        try:
            x = self.coda.get(True, 1.0)
            return x[1]
        except coda.Empty:
            return None


if __name__ == '__main__':
    mac = '00:a0:50:9e:2b:a7'
    ble = BLE(mac)
    x = ble.versione()
    if x is not None:
        print(x)
    del(ble)