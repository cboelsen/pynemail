import curses

from .detailpage import DetailPage
from .emailmenu import EmailMenu
from .page import Page
from .utils import fit_text_to_cols


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

    def render(self, window, column):
        extra = 0
        if self.email.unread():
            extra |= curses.A_BOLD
        if self.selected:
            extra |= curses.A_STANDOUT
        from_text = self.email.sender().ljust(self.from_width)
        subject_text = fit_text_to_cols(self.email.subject(), self.subject_width - 1)
        subject_text = subject_text.ljust(self.subject_width)
        text = '{}{}{}'.format(from_text, subject_text, self.email.date())
        window.addstr(column, 1, text, extra)
        flag_x = self.from_width + self.subject_width + self.date_width + 1
        window.addstr(column, flag_x - 1, ' ', extra)
        if self.email.important():
            window.addstr(column, flag_x, 'I', curses.color_pair(3) | extra)
        else:
            window.addstr(column, flag_x, ' ', extra)
        if self.email.replied():
            window.addstr(column, flag_x + 1, 'R', curses.color_pair(2) | extra)
        else:
            window.addstr(column, flag_x + 1, ' ', extra)
        if self.email.deleted():
            window.addstr(column, flag_x + 2, 'X', curses.color_pair(1) | extra)
        else:
            window.addstr(column, flag_x + 2, ' ', extra)
        if self.email.draft():
            window.addstr(column, flag_x + 3, 'D', curses.color_pair(4) | extra)
        else:
            window.addstr(column, flag_x + 3, ' ', extra)


class InboxPage(Page):

    def __init__(self, screen, mail):
        super().__init__()
        self.window = screen.subwin(0, 0)
        self.mail = mail
        self.resize(curses.LINES, curses.COLS)
        self.selected_row = 0
        self.redraw = True

    def _render(self):
        if self.redraw:
            self.window.clear()
        for i, m in enumerate(self.mail[:curses.LINES - 1]):
            if self.redraw or self.selected_row - 1 <= i <= self.selected_row + 1:
                selected = i == self.selected_row
                e = EmailField(m, selected)
                e.resize(self.from_width, curses.COLS)
                e.render(self.window, i + 1)
        if self.redraw:
            heading = '|' + 'FROM'.center(self.from_width - 1) + '|' + 'SUBJECT'.center(e.subject_width - 1) + '|' + 'DATE'.center(e.date_width - 1) + '|' + 'FLAGS'.center(e.flags_width - 1)
            self.window.addstr(0, 0, heading, curses.A_UNDERLINE)
        self.redraw = False

    def _resize(self, h, w):
        self.from_width = max([len(m.sender()) for m in self.mail]) + 1

    def _update_child_pages(self):
        for child_page in self.child_pages:
            if hasattr(child_page, 'emails'):
                child_page.emails = self._selected_emails()

    def _keypress(self, key):
        if key == curses.KEY_UP:
            if self.selected_row > 0:
                self.selected_row -= 1
                self._update_child_pages()
            return False
        elif key == curses.KEY_DOWN:
            if self.selected_row < curses.LINES - 2 and self.selected_row < len(self.mail) - 1:
                self.selected_row += 1
                self._update_child_pages()
            return False
        #elif key == curses.KEY_ENTER:
        elif key == 10:  # ENTER
            page = DetailPage(self.window, self._selected_emails(), self._remove_child_page)
            self.child_pages.append(page)
            return False
        elif key == 9:  # TAB
            page = EmailMenu(self.window, self._selected_emails(), self._remove_child_page)
            self.child_pages.append(page)
            return False
        return True

    def _selected_emails(self):
        return [self.mail[self.selected_row]]

    def _remove_child_page(self, page):
        self.child_pages.remove(page)
        self.redraw = True

    def _refresh(self):
        self.window.refresh()

    def set_mail(self, mail) -> None:
        self.mail = mail
        self._update_child_pages()
