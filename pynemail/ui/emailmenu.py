import curses

from ..email import EmailFlag

from .utils import center
from .widget import Widget


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


def toggle_flag_on_emails(flag, emails):
    get_flag_state = lambda e: flag not in e.flags()
    newstate = get_flag_state(emails[0])
    for e in emails[1:]:
        if newstate != get_flag_state(e):
            newstate = True
            break
    for e in emails:
        e.set_flag(flag, newstate)


class EmailMenu(Widget):

    def __init__(self, window, emails, removeme):
        super().__init__()
        self.height, self.width = 8, 30
        y, x = center(self.height, self.width)
        self.menuwin = window.subwin(self.height, self.width, y, x)
        self.removeme = removeme
        self.selected_row = 0
        self.options = []
        self._set_emails(emails)

    def _render(self):
        for i, menuitem in enumerate(self.options):
            selected = self.selected_row == i
            menuitem.render(selected, i + 1, self.width - 2)
        for j in range(i + 1, self.height - 2):
            self.menuwin.addstr(j + 1, 1, ' ' * (self.width - 2))
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

    def _get_emails(self):
        return self._emails

    def _set_emails(self, emails):
        self._emails = emails
        self.options = [
            MenuOption(self.menuwin, 'Toggle (un)read', lambda: self.toggle_flag(EmailFlag.SEEN)),
            MenuOption(self.menuwin, 'Toggle important', lambda: self.toggle_flag(EmailFlag.FLAGGED)),
            MenuOption(self.menuwin, 'Toggle deleted', lambda: self.toggle_flag(EmailFlag.DELETED)),
        ]
        any_attachments = any([e.attachments() for e in self._emails])
        if any_attachments:
            self.options.append(MenuOption(self.menuwin, "Save attachment(s)", self.save_attachments))

    emails = property(_get_emails, _set_emails)

    def toggle_flag(self, flag):
        toggle_flag_on_emails(flag, self.emails)
        self.removeme(self)

    def save_attachments(self):
        pass
