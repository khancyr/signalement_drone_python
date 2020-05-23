
Code Libre pour l'implémentation du système d'identification électronique drone français
========================================================================================
Ce dépôt contient deux codes d'exemple en Python.
Le premier `signalement.py` permet de générer et d'envoyer des trames d'identification électronique drone depuis un ordinateur sous linux avec les données provenant d'un système utilisant le protocol MAVLINK
Le second `decoder.py` permet de décoder et d'afficher les trames d'identification électronique drone reçu par un ordinateur sous linux.

Auteurs
-------
Ce code a été initialement écrit et publié par Pierre Kancir avec le soutien de Airbot Systems en mai 2020.

Licence
-------

Tout le code est sous licence GPL https://www.gnu.org/licenses/ (ou synthétiquement : https://choosealicense.com/licenses/gpl-3.0/).
En simplifiant **les obligations**:
- Le code est libre dans son utilisation et sa distribution.
- Vous pouvez l'inclure dans vos projets, mais cela étend la licence GPL à votre projet.
- Si vous vendez un module basé sur ce code, vous devez mentionner clairement à votre client que le code est open source et lui proposer un accès au code source, y compris vos modifications du code originel.
- Le code ne peut pas être reliciencié.


# Prérequis

Le code suivant a été testé sous Ubuntu 20.04. Veuillez adapter les instructions pour votre distribution linux préféré.
Windows **n'est pas supporté** pour l'instant

## Installation de paquets python


    sudo pip3 install -U scapy pymavlink pandas future

Falcultatif:
Vous pouvez installer airmon-ng pour plus de facilité pour gérer votre carte wifi


    sudo apt install airmon-ng

# Utilisation du code
Afin de pouvoir envoyer des trames Wifi modifié et en recevoir facilement, il est nécessaire de passer votre carte wifi en mode monitor.

## Avec airmon-ng
Dans les commandes suivantes remplacer `wlp1s0` par le nom de votre wifi.

    sudo airmon-ng start wlp1s0
    sudo airmon-ng check kill

### Vérification
Vous pouvez vérifier avec `iwconfig` que votre carte wifi est bien passé en mode monitor. Dans mon cas, ça donne :


### Passage sur le channel 6 du Wifi

    sudo iwconfig wlp1s0mon channel 6


## Retour à la normale

    sudo airmon-ng stop wlp1s0mon

### Redemarrage de NetworkManager

    sudo service network-manager restart

## Sans airmon-ng
Avec les commandes de base linux, vous pouvez aussi passer en mode monitor:

    sudo ifconfig wlp1s0 down
    sudo systemctl stop wpa_supplicant.service
    sudo iwconfig wlp1s0 mode Monitor
    sudo ifconfig wlp1s0 up


### Retour à la normale

    sudo ifconfig wlp1s0 down
    sudo iwconfig wlp1s0 mode Managed
    sudo ifconfig wlp1s0 up
    sudo service network-manager restart


## Signalement.py

Modifier les informations :
- `SSID` : le ssid (nom) du point d'accés wifi que vous allez créer
- `iface` : l'interface réseau à utiliser, dans mon cas wlp1s0mon
- `ender_mac` : l'address mac du votre carte wifi, ou l'address mac que vous souhaitez.

Modifier ensuite la source des informations MAVLink. Par default, le programme se connecte sur le port 14550 en UDP.
Vous pouvez par exemple utilisez le simulateur d'ArduPilot SITL en suivant les instructions ici : https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html

Lancez ensuite le programme avec:

    sudo python3 signalement.py



# Observation des trames avec Wireshark
Installer wireshark.
Sous Ubuntu :

    sudo apt install wireshark

Passez votre carte wifi en mode monitor comme expliqué précédemment et lancer Wireshark en mode administrateur :

    sudo wireshark

Sélectionnez votre interface wifi en mode monitor, dans mon cas wlp1s0mon or wlp1s0.
Dans la barre de filtre, pour voir toutes les trames wifi beacon que vous captez, utilisez :

    wlan.fc.type_subtype == 0x0008

Pour filtrer seulement celle de votre appareil, utilisez :

    wlan.fc.type_subtype == 0x0008 and wlan.ssid contains ILLEGAL_DRONE

Ou ILLEGAL_DRONE est le ssid que vous avez renseigné sur votre émetteur pour l'identification drone.
Pour filtrer seulement celles pour l'identification drone, utilisez:

    wlan.tag.oui == 0x6a5c35

