"""
Implements the game server

On connect, the server sends tokens_center, dices_val, characters, areas and active_player
Then, the communication with the client is made through the ClientHandler
"""

import asyncore
import math
import random
import time

import comm
import game


class ClientHandler(asyncore.dispatcher):
    """
    Handles the communications for a client
    """

    def __init__(self, s, i):
        """
        Args:
            s (Server):
            i (int):
        """
        super().__init__(s.clients[i])
        self.server = s
        self.i = i

    def handle_read(self):
        """
        Called when the client sends data.

        The message should be a list, where the first item is a string specifying the client request:
            'token': the client moved it's token, send the new token coordinates to every other client
            'dices': the client rolled the dices, notify every client and send the dice values
            'reveal': the client revealed it's character, notify every client
            'turn': the client ended it's turn, notify every client
            'draw': Todo

        Returns:
            None
        """
        msg = comm.recv(self)
        if msg == b'':
            print("Lost client {0}".format(game.PLAYERS[self.i][0]))
            self.server.clients[self.i] = None
            self.close()
            return

        if msg[0] == 'token':
            print("Player {0} moved it's {1} token"
                  .format(game.PLAYERS[self.i][0], 'second' if msg[1] % 2 else 'first'))
            self.server.tokens_center[msg[1]] = msg[2]
            for client in self.server.clients:
                if client is not None and client is not self.server.clients[self.i]:
                    comm.send(client, msg)
        elif msg[0] == 'dices':
            print("Player {0} rolled the dices".format(game.PLAYERS[self.i][0]))
            self.server.dices_val = [random.randint(1, 4), random.randint(1, 6)]
            for client in self.server.clients:
                if client is not None:
                    comm.send(client, ['dices', self.server.dices_val])
        elif msg[0] == 'reveal':
            print("Player {0} came out of the closet".format(game.PLAYERS[self.i][0]))
            for client in self.server.clients:
                if client is not None:
                    comm.send(client, ['reveal', self.i])
        elif msg[0] == 'turn':
            print("Player {0} ended it's turn".format(game.PLAYERS[self.i][0]))
            self.server.active_player = (self.server.active_player + 1) % game.N_PLAYERS
            for client in self.server.clients:
                if client is not None:
                    comm.send(client, ['turn', self.server.active_player])
        elif msg[0] == 'draw':
            if self.server.cards[msg[1]]:
                print("Player {0} draw a card".format(game.PLAYERS[self.i][0]))
                i_card = self.server.cards[msg[1]].pop()
                for client in self.server.clients:
                    if client is not None:
                        comm.send(client, ['draw', self.i, msg[1], i_card])
            else:
                print("Cannot draw card of type {0}".format(msg[1]))


class Server(asyncore.dispatcher):
    """
    The Server handles incoming connections by giving them a GameHandler.
    It also maintains the game data.

    Attributes:
        clients (list): list of size game.N_PLAYERS, containing the connected clients, or None
        tokens_center (list): the 2 * game.N_PLAYERS token coordinates, stored as tuples of length 2,
            where token_center[2 * i] and token_center[2 * i + 1] belong to player i
        dices_val (list): the dice 4 and dice 6 values, in this order
        characters (list): the playing characters, stored as (alignment, i, flag_revealed),
            the character is then game.Character.CHARACTERS[alignment][i], and is revealed if flag_revealed == True
        areas (list): order of the 6 area cards
        active_player (int): the current player
        cards (list): Todo
    """

    DELAY = 0.1  # Approximate delay between two asyncore.poll

    def __init__(self, host, port):
        """
        Args:
            host:
            port:
        """
        super().__init__()
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(game.N_PLAYERS)
        self.clients = game.N_PLAYERS * [None]

        self.tokens_center = []
        for i in range(game.N_PLAYERS):
            self.tokens_center.append((425 + 30 * math.cos(2 * i * math.pi / game.N_PLAYERS),
                                       270 + 30 * math.sin(2 * i * math.pi / game.N_PLAYERS)))
            self.tokens_center.append((60 + 30 * (i % (game.N_PLAYERS / 2)),
                                       430 + 30 * (i // (game.N_PLAYERS / 2))))

        self.dices_val = [random.randint(1, 4), random.randint(1, 6)]

        self.characters = []
        if game.N_PLAYERS >= 7:  # Removing Bob for 7 and 8 players
            game.Character.CHARACTERS[1 + 0].pop(4)
        for align in (0, 1, 2):
            n_total = len(game.Character.CHARACTERS[align])
            n_avail = game.Character.CHARACTERS_REPARTITION[game.N_PLAYERS][align]
            self.characters += [(align, i, False) for i in random.sample(range(n_total), n_avail)]
        random.shuffle(self.characters)

        self.areas = list(range(6))
        random.shuffle(self.areas)

        self.active_player = 0  # Todo
        # self.active_player = random.randrange(game.N_PLAYERS)

        self.cards = [list(range(len(game.CardVision.CARDS)))]
        for card in self.cards:
            random.shuffle(card)

        try:
            while True:
                asyncore.poll()
                time.sleep(self.DELAY)
        except KeyboardInterrupt:
            pass

    def handle_accepted(self, sock, addr):
        """
        Called on accepting a new client

        Args:
            sock (socket.socket):
            addr (Tuple[str, int]):

        Returns:
            None
        """

        print("Connection from {0} ...".format(addr), end='', flush=True)
        try:
            i = self.clients.index(None)
        except ValueError:
            print(" denied")
            comm.send(sock, -1)
            return
        print(" granted as player {0}".format(game.PLAYERS[i][0]))
        self.clients[i] = sock
        comm.send(sock, i)
        comm.send(sock, self.tokens_center)
        comm.send(sock, self.dices_val)
        comm.send(sock, self.characters)
        comm.send(sock, self.areas)
        comm.send(sock, self.active_player)
        ClientHandler(self, i)


if __name__ == '__main__':
    Server('', 1616)
