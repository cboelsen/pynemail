import curses
import functools
import math

from ..email import EmailFlag

from .page import Page
from .utils import center, shrink_text_to_cols


class DetailPage(Page):

    def __init__(self, screen, email, removeme):
        super().__init__()
        self.screen = screen
        self.height, self.width = curses.LINES - 6, curses.COLS - 10
        y, x = center(self.height, self.width)
        self.win = curses.newwin(self.height, self.width, y, x)
        self.bodywin = self.win.subwin(self.height - 5, self.width - 4, y + 5, x + 2)
        self.removeme = removeme
        self.email = email

    def _render(self):
        self.win.clear()
        self.win.box()
        body_lines, body_columns = self.bodywin.getmaxyx()
        self.win.addstr(1, 2, 'From:    ' + shrink_text_to_cols(self._email.sender(), body_columns - 9))
        self.win.addstr(2, 2, 'To:      ' + shrink_text_to_cols(self._email.to(), body_columns - 9))
        self.win.addstr(3, 2, 'Subject: ' + shrink_text_to_cols(self._email.subject(), body_columns - 9))
        self.win.hline(4, 1, curses.ACS_HLINE, body_columns + 2)
        self.win.addch(4, 0, curses.ACS_LTEE)
        self.win.addch(4, body_columns + 3, curses.ACS_RTEE)
        for i, line in enumerate(self.lines[body_lines * self.page:body_lines * (self.page + 1) - 1]):
            self.bodywin.addstr(i, 0, line)

    def _keypress(self, key):
        if key == 9:  # TAB
            return False
        elif key == 27:  # ESC
            self.removeme(self)
            return False
        elif key == 339:  # PageUp
            if self.page > 0:
                self.page -= 1
            return False
        elif key == 338:  # PageDn
            if self.page < self.pages - 1:
                self.page += 1
            return False
        return True

    def _resize(self, h, w):
        pass

    def _get_email(self):
        return self._email

    def _set_email(self, email):
        self._email = email
        self.page = 0
        body = self._email.body()
        body_lines, body_columns = self.bodywin.getmaxyx()
        self.lines = list(map(lambda x: x + " " * (body_columns - len(x)), functools.reduce(lambda x, y: x + y, [[x[i:i+body_columns] for i in range(0, len(x), body_columns)] for x in body.expandtabs(4).splitlines()])))
        self.pages = int(math.ceil(len(self.lines) / self.bodywin.getmaxyx()[0]))

    email = property(_get_email, _set_email)

    def _refresh(self):
        self.win.refresh()
        self.bodywin.refresh()

    def toggle_read(self):
        newstate = self._email.unread()
        self._email.set_flag(EmailFlag.READ, newstate)
        self._email.clear()
        self.removeme(self)

    def toggle_important(self):
        newstate = not self._email.important()
        self._email.set_flag(EmailFlag.FLAGGED, newstate)
        self._email.clear()
        self.removeme(self)
