#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Programme d'exemple pour émettre des trames d'identification électronique pour drone
    Ce programme fonction avec des données provenant des systèmes utilisant le protocole mavlink.

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

from __future__ import print_function
from scapy.all import *
import pymavlink.mavutil as mavutil
import time
import struct
from droneID import *

"""
    MODIFIEZ LES INFORMATIONS ICI
"""
SSID = "ILLEGAL_DRONE2"
iface = 'wlp1s0mon'
sender_mac = '2a:2a:2a:2a:2a:2a'

"""
    Pour la connection avec un system mavlink
"""
srcSystem = 1
mav_get = mavutil.mavlink_connection('udpin:0.0.0.0:14550', autoreconnect=True, source_system=srcSystem)


def frame_check_heading(value):
    """Heading in degree from north 0 to 359."""
    return value % 360


def format_frame_data(value, bits):
    """ Convert in 2s complement."""
    if bits == 1:
        return value & 0xFF
    if bits == 2:
        return value & 0xFFFF
    if bits == 4:
        return value & 0xFFFFFFFF


def decode_frame_data(value, bits):
    """ Decode 2s complement."""
    # check that we have a negative number
    if value & (1 << (bits * 4 - 1)):
        if bits == 1:
            return value - 0xFF - 1
        if bits == 2:
            return value - 0xFFFF - 1
        if bits == 4:
            return value - 0xFFFFFFFF - 1


def format_frame_WS84(value):
    # TODO: check  -90 <= lat <= 90
    # Todo: check  -180 < long <= 180
    value = int(value * 1e-2)
    return value

# TEST :
# Mesure      Conversion    Encodage
# 48,15278    4815278       0x00 49 79 AE
# 179,12345   17912345      0x01 11 52 19
# -179,12345  -17912345     0xFE EE AD E7
# -48,15278   -4815278      0xFF B6 86 52
# -128                      0xFF 80
# -127                      0xFF 81
# 128                       0x00 80


curr_lat = 0
curr_lon = 0
past_lat = 0
past_lon = 0
home_lat = 0
home_lon = 0
curr_speed = 0
curr_alt_msl = 0
curr_height = 0
curr_heading = 0
get_home = False
traveled_distance = 0
last_send = 0

# TAKEN FROM MAVPROXY
radius_of_earth = 6378100.0  # in meters
def gps_distance(lat1, lon1, lat2, lon2):
    '''return distance between two points in meters,
    coordinates are in degrees
    thanks to http://www.movable-type.co.uk/scripts/latlong.html'''
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)
    dLat = lat2 - lat1
    dLon = lon2 - lon1

    a = math.sin(0.5*dLat)**2 + math.sin(0.5*dLon)**2 * math.cos(lat1) * math.cos(lat2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
    return radius_of_earth * c


def get_distance_accurate(loc1, loc2):
    """Get ground distance between two locations."""
    return gps_distance(loc1.lat, loc1.lng, loc2.lat, loc2.lng)


def parse_msg(msg):
    global curr_lat, curr_lon, past_lat, past_lon, home_lat, home_lon, curr_speed, curr_height, curr_alt_msl, curr_heading, get_home, traveled_distance
    mtype = msg.get_type()
    if mtype == 'GLOBAL_POSITION_INT':
        past_lat = curr_lat
        past_lon = curr_lon
        curr_lat = msg.lat
        curr_lon = msg.lon
        curr_height = msg.relative_alt * 1e-3
        traveled_distance += get_distance_accurate(mavutil.location(past_lat*1e-7, past_lon*1e-7), mavutil.location(curr_lat*1e-7, curr_lon*1e-7))
    if mtype == 'HOME_POSITION' or mtype == 'GPS_GLOBAL_ORIGIN':
        home_lat = msg.latitude
        home_lon = msg.longitude
        get_home = True
    if mtype == 'VFR_HUD':
        curr_speed = msg.groundspeed
        curr_alt_msl = msg.alt
        curr_heading = msg.heading

    #print("ALT : %d, Speed : %0.2f" % (curr_alt, curr_speed))
    # TODO: fix that
    # if not get_home:
    #     msg = mav_get.mav.messages.get("HOME_POSITION", None)
    #     if msg:
    #         get_home = True


def generate_frame():
    # Create dot11 beacon frame on broadcast from our computer
    dot11 = Dot11(type=0, subtype=8, addr1='ff:ff:ff:ff:ff:ff', addr2=sender_mac, addr3=sender_mac)
    beacon = Dot11Beacon(cap='ESS+privacy')
    essid = Dot11Elt(ID='SSID', info=SSID, len=len(SSID))
    # rsn = Dot11Elt(ID='RSNinfo', info=(
    # '\x01\x00'                 #RSN Version 1
    # '\x00\x0f\xac\x02'         #Group Cipher Suite : 00-0f-ac TKIP
    # '\x02\x00'                 #2 Pairwise Cipher Suites (next two lines)
    # '\x00\x0f\xac\x04'         #AES Cipher
    # '\x00\x0f\xac\x02'         #TKIP Cipher
    # '\x01\x00'                 #1 Authentication Key Managment Suite (line below)
    # '\x00\x0f\xac\x02'         #Pre-Shared Key
    # '\x00\x00'))               #RSN Capabilities (no extra capabilities)
    payload = struct.pack('b', FRAME_VS_TYPE)

    payload += struct.pack('>bbb', FRAME_PROTOCOL_VERSION_TYPE, FRAME_TLV_LENGTH[FRAME_PROTOCOL_VERSION_TYPE], FRAME_VS_TYPE)

    payload += struct.pack('>bb', FRAME_ID_FR_TYPE, FRAME_TLV_LENGTH[FRAME_ID_FR_TYPE]) + bytes("ILLEGAL_DRONE_APPELEZ_POLICE17", 'utf-8')

    payload += struct.pack('>bbi', FRAME_LATITUDE_TYPE, FRAME_TLV_LENGTH[FRAME_LATITUDE_TYPE], format_frame_WS84(curr_lat))

    payload += struct.pack('>bbi', FRAME_LONGITUDE_TYPE, FRAME_TLV_LENGTH[FRAME_LONGITUDE_TYPE], format_frame_WS84(curr_lon))

    payload += struct.pack('>bbh', FRAME_ALTITUDE_TYPE, FRAME_TLV_LENGTH[FRAME_ALTITUDE_TYPE], int(curr_alt_msl))

    payload += struct.pack('>bbh', FRAME_HEIGTH_TYPE, FRAME_TLV_LENGTH[FRAME_HEIGTH_TYPE], int(curr_height))

    payload += struct.pack('>bbi', FRAME_HOME_LATITUDE_TYPE, FRAME_TLV_LENGTH[FRAME_HOME_LATITUDE_TYPE], format_frame_WS84(home_lat))

    payload += struct.pack('>bbi', FRAME_HOME_LONGITUDE_TYPE, FRAME_TLV_LENGTH[FRAME_HOME_LONGITUDE_TYPE], format_frame_WS84(home_lon))

    payload += struct.pack('>bbb', FRAME_GROUND_SPEED_TYPE, FRAME_TLV_LENGTH[FRAME_GROUND_SPEED_TYPE], int(curr_speed))

    payload += struct.pack('>bbh', FRAME_HEADING_TYPE, FRAME_TLV_LENGTH[FRAME_HEADING_TYPE], int(curr_heading))
    # https://scapy.readthedocs.io/en/latest/api/scapy.layers.dot11.html#scapy.layers.dot11.Dot11EltVendorSpecific
    # vendor frame for beacon
    vendor = Dot11EltVendorSpecific(ID=FRAME_VS, oui=FRAME_OUI, info=payload, len=len(payload)+3)
    # Generate the wifi frame to send and print
    frame = RadioTap()/dot11/beacon/essid/vendor
    #frame.show()
    return frame

while(True):
    m = mav_get.recv_msg()
    if m is not None:
        parse_msg(m)
    current_time = time.time()
    elapse_time = current_time - last_send
    if traveled_distance >= FRAME_DISTANCE_LIMIT or elapse_time >= FRAME_TIME_LIMIT:
        print("Elapse_time %0.2fs" % elapse_time)
        print("Travelled distance : %0.2fm" % traveled_distance)
        print("ALT : %d, Speed : %0.2f" % (curr_height, curr_speed))
        traveled_distance = 0
        past_lat = curr_lat
        past_lon = curr_lon
        sendp(generate_frame(), iface=iface)
        last_send = current_time
    time.sleep(0.01)
