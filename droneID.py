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

FRAME_TIME_LIMIT = 3            # In s
FRAME_DISTANCE_LIMIT = 30       # In m

# data in payload are in  TLV (type - longueur - valeur)
# |  Type    |  Length                 |  Value  |
# |----------|-------------------------|---------|
# |    00    |    Reserved             |    ND   |
# |    01    |    Protocol version     |    1    |
# |    02    |    ID FR                |    30   |
# |    03    |    ID ANSI CTA 2063 UAS |    ND   |
# |    04    |    Latitude             |    4    |
# |    05    |    Longitude            |    4    |
# |    06    |    Altitude             |    2    |
# |    07    |    Hauteur              |    2    |
# |    08    |    Home Latitude        |    4    |
# |    09    |    Home Longitude       |    4    |
# |    10    |    Ground Speed         |    1    |
# |    11    |    Heading              |    2    |

FRAME_PROTOCOL_VERSION_TYPE = 1
FRAME_ID_FR_TYPE = 2
FRAME_LATITUDE_TYPE = 4        # In WS84 in degree * 1e5
FRAME_LONGITUDE_TYPE = 5       # In WS84 in degree * 1e5
FRAME_ALTITUDE_TYPE = 6        # In MSL in m
FRAME_HEIGTH_TYPE = 7          # From Home in m
FRAME_HOME_LATITUDE_TYPE = 8   # In WS84 in degree * 1e5
FRAME_HOME_LONGITUDE_TYPE = 9  # In WS84 in degree * 1e5
FRAME_GROUND_SPEED_TYPE = 10   # In m/s
FRAME_HEADING_TYPE = 11        # Heading in degree from north 0 to 359.

FRAME_TLV_LENGTH = [0, 1, 30, 0, 4, 4, 2, 2, 4, 4, 1, 2]
FRAME_TLV_LENGTH_TYPE = ['b', 'b', 's', 'b', 'i', 'i', 'h', 'h', 'i', 'i', 'b', 'h']
FRAME_COPTER_ID = 3
FRAME_PLANE_ID = 3

FRAME_VS = 0XDD
FRAME_OUI = 0x6A5C35
FRAME_VS_TYPE = 1
FRAME_PAYLOAD_LEN_MAX = 251
