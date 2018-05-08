import curses
import functools


def center(height, width, screen_h=None, screen_w=None):
    screen_h = curses.LINES if screen_h is None else screen_h
    screen_w = curses.COLS if screen_w is None else screen_w
    y = (screen_h - height) // 2
    x = (screen_w - width) // 2
    return y, x


def shrink_text_to_cols(text, cols):
    if len(text) > cols:
        return text[:cols - 3] + '...'
    return text


def _split_line_at_space(line, cols):
    for i, c in enumerate(line[cols-1::-1]):
        if c.isspace():
            return line[:cols-i], line[cols-i:]
    return line[:cols], line[cols:]


def wrap_text_to_cols(text, cols):
    wrapped_text = []
    for line in text.expandtabs(4).splitlines():
        while line:
            l, line = _split_line_at_space(line, cols)
            wrapped_text.append(l)
    return wrapped_text
