import time
import tkinter

import pygame


class Popup(tkinter.Toplevel):
    """
    Implements a popup window.

    The popup may be completed with tkinter widgets and custom event bindings.
    """
    tkinter.Tk().wm_withdraw()  # Hide the master window

    def __init__(self):
        super().__init__()
        self.title('')
        self.wm_resizable(False, False)
        self.wm_attributes('-topmost', True)
        self.wm_attributes('-type', 'splash')

        self._open = False

    def show(self):
        """
        Shows the popup window.

        Discards all pygame events, so that the main windows is not considered as unresponsive by the window manager.

        Returns:
            None
        """
        self._open = True
        while self._open:
            self.update_idletasks()
            self.update()
            time.sleep(0.1)
            pygame.event.clear()

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
