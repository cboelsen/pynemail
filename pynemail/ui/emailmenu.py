import curses

from ..email import EmailFlag

from .page import Page
from .utils import center


class MenuOption:

    def __init__(self, win, text, action):
        self.window = win
        self.text = text
        self.action = action

    def render(self, selected, col, width):
        extra = 0
        if selected:
            extra |= curses.A_STANDOUT
        self.window.addstr(col, 1, self.text.center(width), extra)


class EmailMenu(Page):

    def __init__(self, screen, email, removeme):
        super().__init__()
        self.screen = screen
        self.email = email
        h, w = 4, 30
        y, x = center(h, w)
        self.menuwin = curses.newwin(h, w, y, x)
        self.removeme = removeme
        self.selected_row = 0
        self.options = [
            MenuOption(self.menuwin, 'Toggle (un)read', self.toggle_read),
            MenuOption(self.menuwin, 'Toggle important', self.toggle_important),
        ]

    def _render(self):
        self.menuwin.clear()
        for i, menuitem in enumerate(self.options):
            selected = self.selected_row == i
            menuitem.render(selected, i + 1, 30)
        self.menuwin.box()

    def _keypress(self, key):
        if key == curses.KEY_UP:
            if self.selected_row > 0:
                self.selected_row -= 1
            return False
        elif key == curses.KEY_DOWN:
            if self.selected_row < len(self.options) - 1:
                self.selected_row += 1
            return False
        elif key == 9:  # TAB
            return False
        elif key == 27:
            self.removeme(self)
            return False
        #elif key == curses.KEY_ENTER:
        elif key == 10:  # ENTER
            self._get_selected_option().action()
            return False
        return True

    def _resize(self, h, w):
        pass

    def _refresh(self):
        self.menuwin.refresh()

    def _get_selected_option(self):
        return self.options[self.selected_row]

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
