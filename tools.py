#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

####################################################################
# This file is part of atts.

# Foobar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#####################################################################


import ast
import subprocess


def get_ip_address():
    """La commande en terminal:
    hostname -I
    retourne l'ip locale !!
    """
    
    try:
        IP_CMD = "hostname -I"
        
        ip_long = subprocess.check_output(IP_CMD, shell=True)
        ip = ip_long.decode("utf-8")
        # espace\n à la fin à couper
        ip = ip[:-2]

    except:
        ip = "192.168.0.106"
    print("IP = {} de type {} len {}".format(ip, 
                                               type(ip),
                                               len(ip)))

    return ip

def datagram_decode(data):
    """Decode le message.
    Retourne un dict ou None
    """

    try:
        dec = data.decode("utf-8")
    except:
        #print("Décodage UTF-8 impossible")
        dec = data

    try:
        msg = ast.literal_eval(dec)
    except:
        #print("ast.literal_eval impossible")
        msg = dec

    if isinstance(msg, dict):
        return msg
    else:
        #print("Message reçu: None")
        return None

if __name__ == "__main__":
    
    get_ip_address()
