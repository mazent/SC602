#! /usr/bin/env python

from __future__ import print_function

import bluepy.btle as bt
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


import utili

class _delega(bt.DefaultDelegate):
    def __init__(self, coda):
        bt.DefaultDelegate.__init__(self)
        self.coda = coda

    def handleNotification(self, cHandle, data):
        self.coda.put((cHandle, data))

def _acaso(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class IOEX(object):

    def __init__(self, mac):
        self.coda = coda.Queue()

        self.crtL = None
        self.crtS = None

        dlg = _delega(self.coda)
        try:
            self.dev = bt.Peripheral(mac)
            self.dev.setMTU(512)

            self.dev.withDelegate(dlg)

            srvz = self.dev.getServices()
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

        except bt.BTLEException:
            self.dev = None

    def __del__(self):
        if self.dev is not None:
            self.dev.disconnect()

    def a_posto(self):
        return self.crtS is not None

    def versione(self, dim=0):
        cmd_ver = {'TS': int(time.time())}
        cmd = json.JSONEncoder().encode(cmd_ver)

        # Aggiungo "X": "..." e il separatore col suo spazio
        if dim > len(cmd) + 3 + 2 + 2 + 2:
            cmd_ver['X'] = _acaso(dim - (len(cmd) + 3 + 2 + 2 + 2))
            cmd = json.JSONEncoder().encode(cmd_ver)

        self.crtS.write(cmd, True)

        try:
            if self.dev.waitForNotifications(.5):
                x = self.coda.get(False)
                return x[1], len(x[1]) + len(cmd)
            else:
                return None
        except coda.Empty:
            return None


if __name__ == '__main__':
    mac = '00:a0:50:9e:2b:a7'
    ble = IOEX(mac)
    if ble.a_posto():
        TOT = 100
        bene = 0
        tot = 0
        inizio = time.clock()
        for _ in range(TOT):
            x = ble.versione(500)
            if x is not None:
                bene += 1
                tot += x[1]
            else:
                print('err versione')
        durata = time.clock() - inizio
        sdurata = utili.stampaDurata(int(round(durata * 1000.0, 0)))
        if TOT == bene:
            milli = round(1000.0 * durata / TOT, 3)
            tput = round(tot / durata, 1)
            kib = round(tot / (durata * 1024), 1)
            print(
                "Eco: OK %d in %s (%.3f ms = %.1f B/s = %.1f KiB/s)" %
                (TOT, sdurata, milli, tput, kib))
        else:
            print(
                "Eco: %d errori su %d [%s]" %
                (TOT - bene, TOT, sdurata))
    del(ble)
