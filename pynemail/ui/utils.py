import curses


def center(height, width):
    y = (curses.LINES - height) // 2
    x = (curses.COLS - width) // 2
    return y, x


def shrink_text_to_cols(text, cols):
    if len(text) > cols:
        return text[:cols - 3] + '...'
    return text
