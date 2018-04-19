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


class Game:

    def __init__(self):
        self.players = {}
        self.somme = 0
        self.reset = 0
        
    def update_game(self, data_ori):
        """data = {client1: {'client':data11},
                   client2: {'client':data2}}"""

        # pour éviter dictionary changed size during iteration
        data = data_ori.copy()
        
        for k, v in data.items():
            if v:
                if 'reset' in v.values():
                    self.somme = 0
                    self.reset = 1
                    print("reset")
        if self.reset == 0:
            self.add_data(data)
        else:
            self.reset = 0

    def add_data(self, data):
        """self.players =
        {('192.168.1.12', 39464): 162,
        ('192.168.1.12', 39466): 162,
        ('192.168.1.12', 39468): 162,
        ('192.168.1.12', 39470): 162}
        """
        # sinon ça pointe vers la même mémoire
        players_old = self.players.copy()

        for k, v in data.items():
            # récup des nums
            if k and v:
                self.players[k] = v['client']

        self.somme = sum(self.players.values())


if __name__ == "__main__":
    data1 = {('192.168.1.12', 42514): {'client': '469'},
             ('192.168.1.12', 42512): {'client': '500'},
             ('192.168.1.12', 42518): {'client': '538'},
             ('192.168.1.12', 42516): {'client': '472'}}

    data2 = {('192.168.1.12', 42514): {'client': '469'},
             ('192.168.1.12', 42512): {'client': '501'},
             ('192.168.1.12', 42518): {'client': '538'},
             ('192.168.1.12', 42516): {'client': '473'}}

    data3 = {('192.168.1.12', 42514): {'client': '50'},
             ('192.168.1.12', 42512): {'client': '10'},
             ('192.168.1.12', 42518): {'client': '22'},
             ('192.168.1.12', 42516): {'client': '33'}}
             
    game = Game()
    game.update_game(data1)
    game.update_game(data1)
    game.update_game(data2)
    game.update_game(data3)
