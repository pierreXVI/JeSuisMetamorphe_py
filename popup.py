import os
import tkinter

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # To hide pygame message
import pygame  # noqa: E402


class Popup(tkinter.Toplevel):
    """
    Implements a popup window.

    The popup may be completed with tkinter widgets and custom event bindings.
    """
    tkinter.Tk().wm_withdraw()  # Hide the master window

    def __init__(self, game):
        super().__init__()
        self.title('')
        self.wm_resizable(False, False)
        self.wm_overrideredirect(True)

        self._game = game
        self._open = False

    def callback(self):
        """
        A callback function, called once per frame

        Returns:
            None
        """
        return

    def show(self):
        """
        Shows the popup window.

        Maintain the Game instance loop but discards all events

        Returns:
            None
        """
        self._open = True
        for token in self._game.owned_tokens:
            token.drop()
        while self._open:
            self.callback()
            self.update_idletasks()
            self.update()
            pygame.event.clear()
            self._game.client.poll()
            self._game.update_display()
            self._game.clock.tick(self._game.FRAME_RATE)

    def center(self):
        """
        Centers the popup window on the user screen.

        Todo: what happens on multiple display ?

        Returns:
            None
        """
        self.master.eval('tk::PlaceWindow {0} center'.format(self))

    def destroy(self):
        """
        Destroys the popup window.

        Returns:
            None
        """
        super().destroy()
        self._open = False
