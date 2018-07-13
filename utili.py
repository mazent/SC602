#!/usr/bin/env python

"""
    Varie
"""

from __future__ import print_function

import binascii
import threading
import random


def validaStringa(x, dimmin=None, dimmax=None):
    """
        Usata sui campi testo per validare che la
        lunghezza sia fra un minimo e un massimo
    """
    esito = False

    if x is None:
        pass
    elif dimmin is None:
        if dimmax is None:
            # Accetto qls dimensione
            esito = True
        elif len(x) > dimmax:
            pass
        else:
            esito = True
    elif len(x) < dimmin:
        pass
    elif dimmax is None:
        esito = True
    elif len(x) > dimmax:
        pass
    else:
        esito = True

    return esito


def validaCampo(x, mini=None, maxi=None):
    """
        Se la stringa x e' un intero, controlla
        che sia tra i due estremi inclusi
    """
    esito = False
    val = None
    while True:
        if x is None:
            break

        if len(x) == 0:
            break

        try:
            val = int(x)
        except ValueError:
            try:
                val = int(x, 16)
            except ValueError:
                pass

        if val is None:
            break

        # Entro i limiti?
        if mini is None:
            pass
        elif val < mini:
            break
        else:
            pass

        if maxi is None:
            pass
        elif val > maxi:
            break
        else:
            pass

        esito = True
        break

    return esito, val


def strVer(vn):
    """
        Converte la versione del fw in stringa
    """

    vmag = vn >> 24
    vmin = vn & 0xFFFFFF

    ver = str(vmag)
    ver += "."
    ver += str(vmin)

    return ver


def verStr(vs):
    """
        Converte una stringa x.y nella versione del fw
    """
    magg, dummy, mino = vs.partition('.')

    esito, ver = validaCampo(magg, 0, 255)

    if not esito:
        return False, 0

    esito, v2 = validaCampo(mino, 0, 0xFFFFFF)
    if not esito:
        return False, 0

    ver <<= 24
    ver += v2

    return True, ver


def intEsa(val, cifre=8):
    """
        Converte un valore in stringa esadecimale senza 0x iniziale
    """
    x = hex(val)
    s = x[2:]
    ver = ""
    dim = len(s)
    while dim < cifre:
        ver += "0"
        dim += 1

    ver += s.upper()

    return ver


def StampaEsa(cosa, titolo=''):
    """
        Stampa un dato binario
    """
    if cosa is None:
        print('<vuoto>')
    else:
        print(titolo, binascii.hexlify(cosa))
        # print ''.join('{:02X.}'.format(x) for x in cosa)


def gomsm(conv, div):
    """
        Converte un tempo in millisecondi in una stringa
    """
    if conv[-1] < div[0]:
        return conv
    else:
        resto = conv[-1] % div[0]
        qznt = conv[-1] // div[0]

        conv = conv[:len(conv) - 1]
        conv = conv + (resto, qznt)

        div = div[1:]

        if len(div):
            return gomsm(conv, div)
        else:
            return conv


def stampaDurata(milli):
    """
        Converte un numero di millisecondi in una stringa
        (giorni, ore, minuti, secondi millisecondi)
    """
    x = gomsm((milli,), (1000, 60, 60, 24))
    unita = ('ms', 's', 'm', 'o', 'g')

    durata = ""
    for i in range(0, len(x)):
        if len(durata):
            durata = ' ' + durata
        durata = str(x[i]) + unita[i] + durata
    return durata


def baMac(mac):
    """
        Converte da mac a bytearray
    """
    componenti = mac.split(':')
    if len(componenti) != 6:
        return None
    else:
        mac = bytearray()
        for elem in componenti:
            esito, val = validaCampo('0x' + elem, 0, 255)
            if esito:
                mac += bytearray([val])
            else:
                mac = None
                break

        return mac


class problema(Exception):

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


class periodico(threading.Thread):

    def __init__(self, funzione, param=None):
        threading.Thread.__init__(self)

        self.secondi = None
        self.funzione = funzione
        self.param = param

        self.evento = threading.Event()

    def run(self):
        while True:
            esci = self.evento.wait(self.secondi)
            if esci:
                break

            if self.param is not None:
                self.funzione(self.param)
            else:
                self.funzione()

    def avvia(self, secondi):
        if self.secondi is None:
            self.secondi = secondi
            self.start()

    def termina(self):
        if self.secondi is not None:
            self.evento.set()
            self.join()
            self.secondi = None

    def attivo(self):
        return self.secondi is not None

def stampaTabulare(pos, dati, prec=4):
    """
        Stampa il bytearray dati incolonnando per 16
        prec e' il numero di cifre di pos
    """
    testa_riga = '%0' + str(prec) + 'X '

    print('00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F'.rjust(prec + (3 * 16)))
    primo = pos & 0xFFFFFFF0

    bianchi = pos & 0x0000000F
    riga = testa_riga % primo
    while bianchi:
        riga += '   '
        bianchi -= 1

    conta = pos & 0x0000000F
    for x in dati:
        riga += '%02X ' % (x)
        conta += 1
        if conta == 16:
            print(riga)
            primo += 16
            riga = testa_riga % primo
            conta = 0
    if conta:
        print(riga)

def byte_casuali(quanti):
    vc = bytearray()
    for _ in range(quanti):
        x = random.randint(0, 255)
        vc.append(x)
    return vc

# Converte una stringa esadecimale di tipo xx-yy-zz
# nel bytearray [xx, yy, zz]

def ba_da_esa(esa, sep='-'):
    ba = bytearray()
    x = esa.split(sep)
    try:
        for y in x:
            ba.append(int(y, base=16))
    except ValueError:
        ba = None

    return ba

# Converte un bytearray [xx, yy, zz] in
# stringa esadecimale "xx-yy-zz"

def esa_da_ba(ba, sep='-'):
    esa = ''
    for i in range(len(ba) - 1):
        esa += '%02X' % ba[i]
        esa += sep
    esa += '%02X' % ba[len(ba) - 1]

    return esa

def cod_finto(dim):
    base = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    cod = ''
    while dim > 0:
        random.shuffle(base)
        dimp = min(dim, len(base))
        cod = cod + ''.join(base[:dimp])
        dim -= dimp

    return cod

# Crea un finto codice scheda

def cod_scheda(pre):
    return pre + 'py' + cod_finto(6)

# Crea un finto codice prodotto

def cod_prod():
    return cod_finto(12)


if __name__ == '__main__':
    millisec = 1234567890
    print(gomsm((millisec,), (1000, 60, 60, 24)))
    print(stampaDurata(millisec))
