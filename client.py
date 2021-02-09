import select
import socket

import comm
import game


class Client(socket.socket):
    """
    Game client

    Attributes:
        i (int): the client index in the server
        game (game.GameThread): the running content
    """

    def __init__(self, host, port):
        """
        Args:
            host (str):
            port (int):
        """
        super().__init__()
        self.connect((host, port))

        self.setblocking(True)
        try:
            self.i = comm.recv(self)
        except ConnectionRefusedError:
            self.i = b''
        if self.i == b'' or self.i == -1:
            self.close()
            print("Cannot reach the server")
            return
        tokens_center = comm.recv(self)
        dices_val = comm.recv(self)
        characters = comm.recv(self)
        areas = comm.recv(self)
        active_player = comm.recv(self)
        self.setblocking(False)

        self.game = game.Game(self, tokens_center, dices_val, characters, areas, active_player)
        self.game.run()

    def poll(self):
        """
        Tries to read data from the server

        Returns:
            None
        """

        r, _, _ = select.select([self], [], [], 0)
        if r:
            msg = comm.recv(self)
            if msg == b'':
                print("Lost connection from server")
                self.close()
                return

            if msg[0] == 'token':
                self.game.tokens[msg[1]].center = msg[2]
            elif msg[0] == 'dices':
                self.game.dices[0].roll_to(msg[1][0])
                self.game.dices[1].roll_to(msg[1][1])
            elif msg[0] == 'reveal':
                self.game.characters[msg[1]].revealed = True
            elif msg[0] == 'turn':
                self.game.active_player.i = msg[1]
            elif msg[0] == 'draw':
                if msg[2] == 1 and self.i == msg[1]:
                    self.send_vision(msg[3], self.game.cards[msg[2]].draw(msg[3], msg[1]))
                else:
                    self.game.cards[msg[2]].draw(msg[3], msg[1])
            elif msg[0] == 'vision':
                self.game.cards[0].answer(msg[1], msg[2])
            else:
                print(msg)

    def close(self):
        """
        Closes the client

        Returns:
            None
        """
        self.game.running = False
        super().close()

    def send_token(self, i):
        """
        Send the coordinates of the token i

        Args:
            i (int):

        Returns:
            None
        """
        comm.send(self, ['token', i, self.game.tokens[i].center])

    def roll_dice(self):
        """
        Ask for a dice roll

        Returns:
            None
        """
        comm.send(self, ['dices'])

    def reveal(self):
        """
        Ask to reveal the character

        Returns:
            None
        """
        comm.send(self, ['reveal'])

    def end_turn(self):
        """
        Ask to end the turn

        Returns:
            None
        """
        comm.send(self, ['turn'])

    def draw(self, i):
        """
        Ask to draw a card from pile i

        Args:
            i (int):

        Returns:
            None
        """
        comm.send(self, ['draw', i])

    def send_vision(self, i_vision, i_player):
        """
        Send the vision i_vision to the player i_player

        Args:
            i_vision (int):
            i_player (int):

        Returns:
            None
        """
        comm.send(self, ['vision', i_vision, i_player])


if __name__ == '__main__':
    Client('', 1616)
