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

    def show(self):
        """
        Shows the popup window.

        Returns:
            None
        """
        self.wait_window(self)

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

        Discards all events, so that the main pygame loop will ignore events that occurred during the popup lifetime.

        Returns:
            None
        """
        super().destroy()
        try:
            pygame.event.clear()
        except pygame.error:
            pass
