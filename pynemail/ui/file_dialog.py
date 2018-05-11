import curses

from .widget import Widget
from .utils import center


class FileDialog(Widget):

    def __init__(self, dirpath, removeme, filename=None):
        self._dirpath = dirpath
        self._filename = filename
        self._removeme = removeme
        self._height, self._width = 12, 60
        y, x = center(self.height, self.width)
        self.window = window.subwin(self.height, self.width, y, x)

    def _render(self):
        self.window.box()

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
        self.window.refresh()
