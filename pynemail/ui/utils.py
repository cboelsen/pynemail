import contextlib
import curses
import functools
import urwid


def center(height, width, screen_h=None, screen_w=None):
    screen_h = curses.LINES if screen_h is None else screen_h
    screen_w = curses.COLS if screen_w is None else screen_w
    y = (screen_h - height) // 2
    x = (screen_w - width) // 2
    return y, x


def fit_text_to_cols(text, cols):
    if len(text) > cols:
        return text[:cols - 3] + '...'
    return text + (' ' * (cols - len(text)))


def _split_line_at_space_if_possible(line, cols):
    for i, c in enumerate(line[cols-1::-1]):
        if c.isspace():
            return line[:cols-i], line[cols-i:]
    return line[:cols], line[cols:]


def wrap_text_to_cols(text, cols):
    wrapped_text = []
    append_line = lambda l: wrapped_text.append(l + ' ' * (cols - len(l)))
    for line in text.expandtabs(4).splitlines():
        while len(line) > cols:
            l, line = _split_line_at_space_if_possible(line, cols)
            append_line(l)
        append_line(line)
    return wrapped_text


@contextlib.contextmanager
def hidden_cursor():
    urwid.escape.ORIGINAL_SHOW_CURSOR = urwid.escape.SHOW_CURSOR
    urwid.escape.SHOW_CURSOR = ''
    try:
        yield
    finally:
        #urwid.escape.SHOW_CURSOR = urwid.escape.ORIGINAL_SHOW_CURSOR
        urwid.escape.SHOW_CURSOR = urwid.escape.ESC + "[?25h"


@contextlib.contextmanager
def shown_cursor():
    try:
        urwid.escape.SHOW_CURSOR = urwid.escape.ORIGINAL_SHOW_CURSOR
    except AttributeError:
        raise Exception('you have to hide the cursor before you can show it again')
    try:
        yield
    finally:
        urwid.escape.SHOW_CURSOR = ''
