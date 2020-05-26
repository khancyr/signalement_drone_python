#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Programme d'exemple pour émettre des trames d'identification électronique pour drone

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    Ce code a été initialement écrit et publié par Pierre Kancir avec le soutien de Airbot Systems en mai 2020.
"""
import threading
import os
import time
import random
from scapy.all import *
import struct
import pandas
from droneID import *

"""
    Changer votre interface wifi ici
"""
interface = "wlp1s0mon"

# initialize the networks dataframe that will contain all access points nearby
TVL = pandas.DataFrame(columns=["T", "L", "V"])
TVL.set_index("T", inplace=True)
frame_num = 0


def hopper(iface):
    """ Pour changer le channel wifi."""
    n = 1
    stop_hopper = False
    while not stop_hopper:
        time.sleep(0.50)
        #os.system('iwconfig %s channel %d' % (iface, n))
        dig = int(random.random() * 14)
        if dig != 0 and dig != n:
            n = dig


def print_all():
    while True:
        os.system("clear")
        print(TVL)
        time.sleep(1)


def findSSID(pkt):
    if pkt.haslayer(Dot11Beacon):
        frame = pkt.getlayer(Dot11EltVendorSpecific)
        if frame.oui == 0x6A5C35:
            #print("ID %d, OUI %s, len %d" % ((frame.ID), hex(frame.oui), (frame.len)))
            # start at 6 because frame first 5 bytes are OUI+VSTYPE, frame.info containt the OUI but not the last part of the payload...
            count = 0
            payload = frame.original[6:]
            while count < len(payload):
                V = ''
                T, L = struct.unpack_from('>bb', payload, count)
                count += 2
                if T != 2:
                    V = struct.unpack_from('>%s' % FRAME_TLV_LENGTH_TYPE[T], payload, count)[0]
                else:
                    V = struct.unpack_from('>30s', payload, count)[0].decode('utf-8')
                #print("T: %s, L: %s, V:%s" % (T, L, V))
                count += L
                TVL.loc[T] = (L, V)


if __name__ == "__main__":
    # thread = threading.Thread(target=hopper, args=(interface, ), name="hopper")
    # thread.daemon = True
    # thread.start()
    printer = Thread(target=print_all)
    printer.daemon = True
    printer.start()
    sniff(iface=interface, prn=findSSID, lfilter=lambda x: x.haslayer(Dot11Beacon), monitor=True)
