import curses


def center(height, width):
    y = (curses.LINES - height) // 2
    x = (curses.COLS - width) // 2
    return y, x
