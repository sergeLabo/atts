#!/usr/bin/python3
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

import socket
from time import sleep

import threading
import json

# Variable globale
QUEUE = []


class LabTcpClient:
    """Envoi et réception sur le même socket en TCP.
    Toutes les méthodes sont sans try.
    """

    def __init__(self, ip, port, buffer_size=1024):

        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size
        self.server_address = (ip, port)
        self.data = None
        self.sock = None
        self.create_socket()

    def create_socket(self):
        """Création du socket sans try, et avec connexion."""

        while not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect_sock()
            print("    Création du socket client {}".format(self.server_address))
            sleep(0.1)

    def connect_sock(self):
        """Connexion de la socket, si ok retoune 1 sinon None"""

        try:
            self.sock.connect(self.server_address)
            return 1
        except:
            print("        Connexion impossible du client sur {}".
                  format(self.server_address))
            return None

    def send(self, msg):
        """Envoi d'un message, avec send, msg doit être encodé avant."""

        # Création d'un socket si besoin
        if not self.sock:
            self.create_socket()

        # Envoi
        try:
            self.sock.send(msg)
        except:
            print("Envoi raté: {}".format(msg))
            # Nouvelle création d'une socket
            self.sock.close()
            self.sock = None

    def reconnect(self):
        """Reconnexion."""

        self.sock = None
        self.create_socket()

    def close_sock(self):
        """Fermeture de la socket."""

        try:
            self.sock.close()
        except:
            print("La socket client est déjà close")

        self.sock = None

    def listen(self):
        """Retourne les data brutes reçues."""

        raw_data = None

        raw_data = self.sock.recv(self.buffer_size)

        return raw_data


class MultipleClients:
    global QUEUE
    
    def __init__(self,ip , port, n):
        self.ip = ip
        self.port = port
        self.n = n
        self.clients = []
        self.multiple_clients()
        self.somme = 0
        self.somme_thread()
        
    def somme_thread(self):
        t = threading.Thread(target=self.somme_loop)
        t.start()
        
    def somme_loop(self):
        while 1:
            self.get_somme()
            print(self.somme)
            sleep(1)
            
    def get_somme(self):
        global QUEUE
        self.somme = sum(QUEUE)
        QUEUE = []

    def queue_get_all(self):
        global QUEUE
        result_list = []
        while not QUEUE.empty():
            result_list.append(QUEUE.get())
        return result_list
    
    def multiple_clients(self):
        for i in range(self.n):
            self.client_thread(i)
            sleep(0.1)
            
    def client_thread(self, i):
        t = threading.Thread(target=self.one_client)
        self.clients.append(t)
        t.start()

    def one_client(self):
        global QUEUE
        
        client = LabTcpClient(self.ip, self.port)
        toto = json.dumps({"client": "reset"})
        data = toto.encode("utf-8")
        client.send(data)

        for num in range(999999):

            if len(QUEUE) == 4:
                del QUEUE[0]
            if len(QUEUE) > 4:
                QUEUE = []
                
            QUEUE.append(num)
            
            truc = json.dumps({"client": num})
            data = truc.encode("utf-8")
            sleep(0.0166)
            client.send(data)
            
        clt.close_sock()

        
def test(ip, port, length):
    
    if length == "long":
        rep = ""
    elif length == "court":
        rep = ""
    else:
        print("""
Usage:
python3 client_test.py ip port court
ou
python3 client_test.py ip port long
""")
        os._exit(0)
        
    clt = LabTcpClient(ip, int(port))

    int_list = [x for x in range(999999)]
    for num in int_list:
        print("Envoi", num)
        truc = json.dumps({"client": rep + str(num)})
        data = truc.encode("utf-8")
        sleep(0.0166)
        clt.send(data)
            
    clt.close_sock()

    
if __name__ == "__main__":

    MultipleClients("192.168.1.12" , 8000, 4)
