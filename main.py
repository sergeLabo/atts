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


"""

sans twisted, sans asyncio
avec socketserver, en python3

AttsApp ---------> config
        |
      crée
        |
        MainScreen
                |
               Choice crée objet
                 |
               Network Serveur
                 |   lance ThreadedTCPServer
                 |
                 |   PLAYERSDATA dictionnaire en variable globale
                 |   pour échange  data
                 |   entre ThreadedTCPRequestHandler
                 |   et Network
                 |
                 |   Clock update rythme le jeu
                 ou
                 |
               Network Client
                 |
               hérite de
                 |
               MulticastIpSender


doc lien donné par doc officielle sur super()
https://rhettinger.wordpress.com/2011/05/26/super-considered-super/

"""


from os import _exit
from time import time, sleep
from threading import Thread
import socketserver
from json import dumps

import kivy
kivy.require('1.10.0')
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.clock import Clock

from tools import datagram_decode, get_ip_address
from labmulticast import Multicast
from game import Game

# variable globale
PLAYERSDATA = {}

class MulticastIpSender(Multicast):
    """Envoi de l'adresse ip de ce server à tous les clients"""

    def __init__(self, config):

        print("Lancement de la boucle Multicast")
        self.config = config
        self.multi_ip = self.config.get('network', 'multi_ip')
        self.multi_port = int(self.config.get('network', 'multi_port'))
        self.multi_addr = self.multi_ip, self.multi_port
        print("Adresse Multicast:", self.multi_addr)

        super().__init__(self.multi_ip, self.multi_port)

        # Lancement de l'envoi permanent
        self.toujours = 1
        self.ip_send_thread()

    def ip_send(self):
        tcp_ip = get_ip_address()
        tcp_port = int(self.config.get('network', 'tcp_port'))

        m = {"TCP Adress": (tcp_ip, tcp_port)}
        msg = dumps(m).encode("utf-8")

        while self.toujours:
            sleep(1)
            self.send_to(msg, self.multi_addr)

    def ip_send_thread(self):
        self.thread_m = Thread(target=self.ip_send)
        self.thread_m.daemon = True
        self.thread_m.start()

    def stop(self):
        print("Stop du thread multicast")
        self.toujours = None
        print("Thread multicast stoppé")

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """Reçois les datas de chaque client
    cur_thread = threading.current_thread()
    response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
    self.request.sendall(response)
    """

    def handle(self):
        global PLAYERSDATA

        while 1:
            sleep(0.001)
            data = self.request.recv(1024).decode("utf-8")

            if not self.client_address in PLAYERSDATA:
                PLAYERSDATA[self.client_address] = None

            if data:
                data_dec = datagram_decode(data)

                # set dans le dict et la pile
                if self.client_address:
                    PLAYERSDATA[self.client_address] = data_dec

class ThreadedTCPServer(socketserver.ThreadingMixIn,
                        socketserver.TCPServer):
    def __enter__(self):
        print('entering')
        return self

    def __exit__(self, exc_t, exc_v, trace):
        print('exiting')

class Network:

    def __init__(self, config):
        """ip, port = self.svr.server_address"""

        self.config = config

        freq = int(self.config.get('network', 'freq'))
        self.set_tempo(freq)

        self.tcp_ip = get_ip_address()
        self.tcp_port = int(self.config.get('network', 'tcp_port'))

        # Création du Multicast
        self.multi_sender = MulticastIpSender(config)

        # Asynchronous Mixins TCP Server
        self.svr = None
        self.asynchronous_mixins_tcp_server()

        # Rythme du jeu
        self.event = None
        self.start_clock()
        self.test = 0

        # Jeu
        self.game = Game()

        # FPS
        self.t = time()
        self.fps = 0

    def start_clock(self):
        """Nice, it's work"""

        if self.event:
            self.event.cancel()
        self.event = Clock.schedule_interval(self.network_update,
                                             self.tempo)

    def set_tempo(self, freq):
        self.tempo = 1 / freq
        print("Rafraississement du jeu tous les", self.tempo)

    def asynchronous_mixins_tcp_server(self):
        """Deamon du server TCP"""

        self.svr = ThreadedTCPServer((self.tcp_ip, self.tcp_port),
                                      ThreadedTCPRequestHandler)
        with self.svr:
            # Start a thread with the server
            # That thread will then start one more thread for each request
            self.svr_thread = Thread(target=self.svr.serve_forever)

            # Exit the server thread when the main thread terminates
            self.svr_thread.daemon = True
            self.svr_thread.start()
            print("Server loop running in thread:", self.svr_thread.name)

    def stop(self):
        """Termine le with self.svr:"""

        self.svr = None
        print("Server loop running in thread killed")

    def network_update(self, dt):
        """Actualisation par Clock"""

        global PLAYERSDATA

        self.game.update_game(PLAYERSDATA)
        self.fps_update()

    def fps_update(self):
        self.fps += 1
        t = time()
        if t - self.t > 1:
            print("FPS:", self.fps)
            print(self.game.somme)
            self.affichage_provisoire()
            self.fps = 0
            self.t = t

    def affichage_provisoire(self):
        sm = self.get_screen_manager()
        info = "Somme " + str(self.game.somme) + "\nFPS " + str(self.fps)
        sm.current_screen.info = str(info)

    def get_screen_manager(self):
        return AttsApp.get_running_app().screen_manager

class Choice:
    """Permet de choisir server ou client"""
    pass

class Client:
    """Le client qui reçoit des requêtes au server"""
    pass
    
class MainScreen(Screen):
    """Ecran principal"""

    info = StringProperty()

    def __init__(self, **kwargs):
        """
        def __init__(self, **kwargs):
            super(MainScreen, self).__init__(**kwargs)
        """

        super().__init__(**kwargs)

        # Récup config
        self.config = AttsApp.get_running_app().config

        # L'objet jeu
        self.network = Network(self.config)

        print("Initialisation de MainScreen ok")

SCREENS = { 0: (MainScreen, "Main")}

class AttsApp(App):

    def build(self, **kwargs):
        """Exécuté en premier après run()"""

        # Creation des ecrans
        self.screen_manager = ScreenManager()
        for i in range(len(SCREENS)):
            self.screen_manager.add_widget(SCREENS[i][0](name=SCREENS[i][1]))

        return self.screen_manager

    def on_start(self):
        """Exécuté apres build()"""
        pass

    def build_config(self, config):
        """Si le fichier *.ini n'existe pas,
        il est créé avec ces valeurs par défaut.
        Si il manque seulement des lignes, il ne fait rien !
        """

        config.setdefaults('network',
                            { 'multi_ip': '224.0.0.11',
                              'multi_port': '18888',
                              'tcp_port': '8000',
                              'freq': '60'})

        config.setdefaults('kivy',
                            { 'log_level': 'debug',
                              'log_name': 'androidserver_%y-%m-%d_%_.txt',
                              'log_dir': '/toto',
                              'log_enable': '1'})

        config.setdefaults('postproc',
                            { 'double_tap_time': 250,
                              'double_tap_distance': 20})

    def build_settings(self, settings):
        """Construit l'interface de l'écran Options,
        pour  le serveur seul, Kivy est par défaut,
        appelé par app.open_settings() dans .kv
        """

        data =  """[{"type": "title", "title":"Réseau"},
                            {  "type":    "numeric",
                                "title":   "Fréquence",
                                "desc":    "Fréquence entre 1 et 60 Hz",
                                "section": "network",
                                "key":     "freq"},

                    {"type": "title", "title":"Réseau"},
                            {   "type":    "string",
                                "title":   "IP Multicast",
                                "desc":    "IP Multicast",
                                "section": "network",
                                "key":     "multi_ip"},

                    {"type": "title", "title":"Réseau"},
                            {   "type":    "numeric",
                                "title":   "Port Multicast",
                                "desc":    "Port Multicast",
                                "section": "network",
                                "key":     "multi_port"},

                    {"type": "title", "title":"Réseau"},
                            {   "type":    "numeric",
                                "title":   "TCP Port",
                                "desc":    "TCP Port",
                                "section": "network",
                                "key":     "tcp_port"}
                    ]
                """

        # self.config est le config de build_config
        settings.add_json_panel('AndroidServer', self.config, data=data)

    def on_config_change(self, config, section, key, value):
        """Si modification des options, fonction appelée automatiquement
        """

        freq = int(self.config.get('network', 'freq'))
        menu = self.screen_manager.get_screen("Main")

        if config is self.config:
            token = (section, key)

            # If frequency change
            if token == ('network', 'freq'):
                print("Nouvelle fréquence", freq)

                # Maj self.tempo dans Network
                menu.network.set_tempo(freq)
                menu.network.start()

    def go_mainscreen(self):
        """Retour au menu principal depuis les autres écrans."""

        #if touch.is_double_tap:
        self.screen_manager.current = ("Main")

    def do_quit(self):

        print("Je quitte proprement")
        menu = self.screen_manager.get_screen("Main")

        # Multicast loop
        menu.network.multi_sender.stop()

        # TCP Server TODO
        menu.network.stop()

        # Kivy
        AttsApp.get_running_app().stop()

        # Extinction de tout si ça tourne encore
        print("Fin finale")
        _exit(0)

if __name__ == "__main__":
    """Quand lama fâché, lui toujours faire ainsi."""

    AttsApp().run()
