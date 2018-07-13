#! /usr/bin/env python

from __future__ import print_function

# vedi http://ianharvey.github.io/bluepy-doc/index.html
import bluepy.btle as bt
import json
import time
import random
import string
import sys
import uuid
try:
    # 2
    import Queue as coda
except ImportError:
    # 3
    import queue as coda
import utili


tempo = None
if sys.platform.startswith("win32"):
    tempo = time.clock
else:
    tempo = time.time


class _delega(bt.DefaultDelegate):
    def __init__(self, coda):
        bt.DefaultDelegate.__init__(self)
        self.coda = coda

    def handleNotification(self, cHandle, data):
        self.coda.put((cHandle, data))

def _acaso(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def _luhn_checksum(seq):
    doppio = True if len(seq) % 2 == 0 else False
    sum = 0
    for cif in seq:
        num = int(cif)
        if doppio:
            num *= 2
            if num > 9:
                num -= 9
        sum += num
        doppio = not doppio

    sum = sum % 10
    return seq + str(sum)

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

        # La risposta e' immediata
        try:
            if self.dev.waitForNotifications(1.0):
                x = self.coda.get(False)
                return x[1], len(x[1]) + len(cmd)
            else:
                return None
        except coda.Empty:
            return None

    def preq(self):
        pr = _acaso(5, string.digits)
        cmd_preq = {
            'TS': int(time.time()),
            'TI': str(uuid.uuid4()),
            'MSG': str(uuid.uuid4()),
            'MT': 100,
            'PK': _luhn_checksum(pr),
            'DP': [random.randint(0, 1000), random.randint(0, 1000), random.randint(0, 1000)]
        }

        cmd = json.JSONEncoder().encode(cmd_preq)

        self.crtS.write(cmd, True)



if __name__ == '__main__':
    mac = '00:a0:50:9e:2b:a7'
    ble = IOEX(mac)
    if ble.a_posto():
        ble.preq()
        time.sleep(1)
        # TOT = 50
        # bene = 0
        # tot = 0
        # inizio = tempo()
        # for _ in range(TOT):
        #     x = ble.versione()
        #     #x = ble.versione(500)
        #     if x is not None:
        #         bene += 1
        #         tot += x[1]
        #     else:
        #         print('err versione')
        # durata = tempo() - inizio
        # sdurata = utili.stampaDurata(int(round(durata * 1000.0, 0)))
        # if TOT == bene:
        #     milli = round(1000.0 * durata / TOT, 3)
        #     tput = round(tot / durata, 1)
        #     kib = round(tot / (durata * 1024), 1)
        #     print(
        #         "Eco: OK %d in %s (%.3f ms = %.1f B/s = %.1f KiB/s)" %
        #         (TOT, sdurata, milli, tput, kib))
        # else:
        #     print(
        #         "Eco: %d errori su %d [%s]" %
        #         (TOT - bene, TOT, sdurata))
    del(ble)
