import curses

from .detailpage import DetailPage
from .emailmenu import EmailMenu
from .page import Page


class EmailField:

    def __init__(self, email, selected):
        self.email = email
        self.selected = selected
        self.from_width = 0
        self.subject_width = 0
        self.date_width = 26
        self.flags_width = 6

    def resize(self, from_width, screen_width):
        self.from_width = from_width
        self.subject_width = screen_width - (self.date_width + self.from_width + self.flags_width)

    def flags(self):
        return '{}   '.format(
            'I' if self.email.important() else ' ',
        )

    def render(self, screen, column):
        extra = 0
        if self.email.unread():
            extra |= curses.A_BOLD
        if self.selected:
            extra |= curses.A_STANDOUT
        from_text = self.email.sender().ljust(self.from_width)
        if len(self.email.subject()) > self.subject_width - 1:
            subject_text = self.email.subject()[:self.subject_width - 4] + '...'
        else:
            subject_text = self.email.subject()
        subject_text = subject_text.ljust(self.subject_width)
        text = '{}{}{}'.format(from_text, subject_text, self.email.date())
        screen.addstr(column, 1, text, extra)
        flag_x = self.from_width + self.subject_width + self.date_width + 1
        screen.addstr(column, flag_x - 1, ' ', extra)
        if self.email.important():
            screen.addstr(column, flag_x, 'I', curses.color_pair(3) | extra)
        else:
            screen.addstr(column, flag_x, ' ', extra)
        if self.email.replied():
            screen.addstr(column, flag_x + 1, 'R', curses.color_pair(2) | extra)
        else:
            screen.addstr(column, flag_x + 1, ' ', extra)
        if self.email.deleted():
            screen.addstr(column, flag_x + 2, 'X', curses.color_pair(1) | extra)
        else:
            screen.addstr(column, flag_x + 2, ' ', extra)
        if self.email.draft():
            screen.addstr(column, flag_x + 3, 'D', curses.color_pair(4) | extra)
        else:
            screen.addstr(column, flag_x + 3, ' ', extra)


class InboxPage(Page):

    def __init__(self, screen, mail):
        super().__init__()
        self.screen = screen
        self.mail = mail
        self.resize(curses.LINES, curses.COLS)
        self.selected_row = 0

    def _render(self):
        for i, m in enumerate(self.mail[:curses.LINES]):
            selected = i == self.selected_row
            e = EmailField(m, selected)
            e.resize(self.from_width, curses.COLS)
            e.render(self.screen, i + 1)
        heading = '|' + 'FROM'.center(self.from_width - 1) + '|' + 'SUBJECT'.center(e.subject_width - 1) + '|' + 'DATE'.center(e.date_width - 1) + '|' + 'FLAGS'.center(e.flags_width - 1)
        self.screen.addstr(0, 0, heading, curses.A_UNDERLINE)

    def _resize(self, h, w):
        self.from_width = max([len(m.sender()) for m in self.mail]) + 1

    def _keypress(self, key):
        if key == curses.KEY_UP:
            if self.selected_row > 0:
                self.selected_row -= 1
            return False
        elif key == curses.KEY_DOWN:
            if self.selected_row < curses.LINES - 2 and self.selected_row < len(self.mail) - 1:
                self.selected_row += 1
            return False
        #elif key == curses.KEY_ENTER:
        elif key == 10:  # ENTER
            page = DetailPage(self.screen, self.mail[self.selected_row], self.child_pages.remove)
            self.child_pages.append(page)
            return False
        elif key == 9:  # TAB
            page = EmailMenu(self.screen, self.mail[self.selected_row], self.child_pages.remove)
            self.child_pages.append(page)
            return False
        return True

    def _refresh(self):
        self.screen.refresh()
