import curses
import functools
import math

from typing import Callable

from ..email import EmailFlag, Email

from .page import Page
from .utils import center, fit_text_to_cols, wrap_text_to_cols


class DetailPage(Page):

    def __init__(self, screen: object, email: Email, removeme: Callable[[Page], None]) -> None:
        super().__init__()
        self.screen = screen
        self.height, self.width = curses.LINES - 6, curses.COLS - 10
        self.y, self.x = center(self.height, self.width)
        self.win = curses.newwin(self.height, self.width, self.y, self.x)
        self.bodywin = self.win.subwin(self.height - 5, self.width - 4, self.y + 5, self.x + 2)
        self.removeme = removeme
        self.subject_lines = []
        self.previous_subject_lines = []
        self._set_email(email)

    def _render(self):
        self.win.box()
        body_lines, body_columns = self.bodywin.getmaxyx()
        self.win.addstr(1, 2, 'From:    ' + fit_text_to_cols(self._email.sender(), body_columns - 10))
        self.win.addstr(2, 2, 'To:      ' + fit_text_to_cols(self._email.to(), body_columns - 10))
        self.win.addstr(3, 2, 'Subject: ' + self.subject_lines[0])
        for i, line in enumerate(self.subject_lines[1:]):
            self.win.addstr(4 + i, 1, ' ' * 10 + line + '  ')
        self.win.addstr(len(self.previous_subject_lines) + 3, 1, ' ')
        self.win.addstr(len(self.previous_subject_lines) + 3, body_columns + 2, ' ')
        body_window_y = 3 + len(self.subject_lines)
        self.win.hline(body_window_y, 1, curses.ACS_HLINE, body_columns + 2)
        self.win.addch(body_window_y, 0, curses.ACS_LTEE)
        self.win.addch(body_window_y, body_columns + 3, curses.ACS_RTEE)
        for i, line in enumerate(self.lines[body_lines * self.page:body_lines * (self.page + 1) - 1]):
            self.bodywin.addstr(i, 0, line)
        for j in range(i + 1, body_lines - 1):
            self.bodywin.addstr(j, 0,  ' ' * body_columns)

    def _keypress(self, key):
        if key == 10:  # ENTER
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

    def _resize(self, h: int, w: int) -> None:
        pass

    def _get_email(self) -> Email:
        return self._email

    def _set_email(self, email: Email) -> None:
        self._email = email
        self.page = 0
        body = self._email.body()
        body_lines, body_columns = self.bodywin.getmaxyx()
        self.previous_subject_lines = self.subject_lines
        self.subject_lines = wrap_text_to_cols(self._email.subject(), body_columns - 10)
        if len(self.previous_subject_lines) != len(self.subject_lines):
            self.bodywin = self.win.subwin(self.height - 4 - len(self.subject_lines), self.width - 4, self.y + 4 + len(self.subject_lines), self.x + 2)
            body_lines, body_columns = self.bodywin.getmaxyx()
        self.lines = wrap_text_to_cols(body, body_columns)
        self.pages = int(math.ceil(len(self.lines) / body_lines))

    email = property(_get_email, _set_email)

    def _refresh(self):
        self.win.refresh()
        self.bodywin.refresh()

    def toggle_read(self) -> None:
        newstate = self._email.unread()
        self._email.set_flag(EmailFlag.SEEN, newstate)
        self.removeme(self)

    def toggle_important(self) -> None:
        newstate = not self._email.important()
        self._email.set_flag(EmailFlag.FLAGGED, newstate)
        self.removeme(self)
