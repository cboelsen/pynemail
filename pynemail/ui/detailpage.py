import curses

from ..email import EmailFlag

from .page import Page
from .utils import center


class DetailPage(Page):

    def __init__(self, screen, email, removeme):
        super().__init__()
        self.screen = screen
        self.email = email
        h, w = curses.LINES - 6, curses.COLS - 10
        y, x = center(h, w)
        self.win = curses.newwin(h, w, y, x)
        self.removeme = removeme

    def _render(self):
        self.win.clear()
        self.win.box()

    def _keypress(self, key):
        if key == 9:  # TAB
            return False
        elif key == 27:
            self.removeme(self)
            return False
        return True

    def _resize(self, h, w):
        pass

    def _refresh(self):
        self.win.refresh()

    def toggle_read(self):
        newstate = self.email.unread()
        self.email.set_flag(EmailFlag.READ, newstate)
        self.email.clear()
        self.removeme(self)

    def toggle_important(self):
        newstate = not self.email.important()
        self.email.set_flag(EmailFlag.FLAGGED, newstate)
        self.email.clear()
        self.removeme(self)
