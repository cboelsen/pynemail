import curses
import math

from .detailpage import DetailPage
from .emailmenu import EmailMenu
from .utils import fit_text_to_cols
from .widget import Widget


class EmailField:

    def __init__(self, email, selected):
        self.email = email
        self.selected = selected
        self.from_width = 0
        self.subject_width = 0
        self.date_width = 26
        self.flags_width = 7

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
        if self.email.attachments():
            window.addstr(column, flag_x + 4, 'A', curses.color_pair(4) | extra)
        else:
            window.addstr(column, flag_x + 4, ' ', extra)


class InboxPage(Widget):

    def __init__(self, screen, mail):
        super().__init__()
        self.window = screen.subwin(0, 0)
        self.selected_row = 0
        self.selected_row_start = -1
        self.redraw = True
        self.page = 0
        self.emails_per_page = 1
        self.from_width = 0
        self.set_mail(mail)

    def _mail_on_screen(self):
        return self.mail[self.emails_per_page * self.page:self.emails_per_page * (self.page + 1)]

    def _render(self):
        low, high = self._selected_row_range()
        rendered_mail = self._mail_on_screen()
        for i, m in enumerate(rendered_mail):
            if self.redraw or low - 1 <= i <= high + 1:
                selected = low <= i <= high
                e = EmailField(m, selected)
                e.resize(self.from_width, curses.COLS)
                e.render(self.window, i + 1)
        if self.redraw:
            for j in range(i + 1, self.emails_per_page):
                self.window.addstr(j + 1, 0, ' ' * (curses.COLS - 1))
            heading = '|' + 'FROM'.center(self.from_width - 1) + '|' + 'SUBJECT'.center(e.subject_width - 1) + '|' + 'DATE'.center(e.date_width - 1) + '|' + 'FLAGS'.center(e.flags_width - 1)
            self.window.addstr(0, 0, heading, curses.A_UNDERLINE)
        self.redraw = False

    def _resize(self, h, w):
        self.from_width = max([len(m.sender()) for m in self.mail]) + 1
        self.emails_per_page = h - 1
        self.pages = int(math.ceil(len(self.mail) / self.emails_per_page))

    def _selected_row_range(self):
        if self.selected_row_start == -1:
            return self.selected_row, self.selected_row
        return (self.selected_row, self.selected_row_start) if self.selected_row < self.selected_row_start else (self.selected_row_start, self.selected_row)

    def _selected_emails(self):
        low, high = self._selected_row_range()
        return self._mail_on_screen()[low:high+1]

    def _update_child_pages(self):
        for child_page in self.child_pages:
            if hasattr(child_page, 'emails'):
                child_page.emails = self._selected_emails()

    def _keypress(self, key):
        if key == curses.KEY_UP:
            if self.selected_row > 0:
                self.selected_row -= 1
                self._update_child_pages()
            elif self.page > 0:
                self.page -= 1
                self.selected_row = self.emails_per_page - 1
                self.redraw = True
            return False
        elif key == curses.KEY_DOWN:
            if self.selected_row < len(self._mail_on_screen()) - 1:
                self.selected_row += 1
                self._update_child_pages()
            elif self.page < self.pages - 1:
                self.page += 1
                self.selected_row = 0
                self.redraw = True
            return False
        elif key == 339:  # PageUp
            if self.page > 0:
                self.page -= 1
                self.redraw = True
            return False
        elif key == 338:  # PageDn
            if self.page < self.pages - 1:
                self.page += 1
                mail_on_screen = self._mail_on_screen()
                if self.selected_row >= len(mail_on_screen):
                    self.selected_row = len(mail_on_screen) - 1
                self.redraw = True
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
        elif key == 32:  # SPACE BAR
            if self.selected_row_start == -1:
                self.selected_row_start = self.selected_row
            else:
                self.selected_row_start = -1
                self.redraw = True
        return True

    def _remove_child_page(self, page):
        self.child_pages.remove(page)
        self.redraw = True

    def _refresh(self):
        self.window.refresh()

    def set_mail(self, mail) -> None:
        self.mail = mail
        self.pages = int(math.ceil(len(self.mail) / self.emails_per_page))
        self._update_child_pages()
