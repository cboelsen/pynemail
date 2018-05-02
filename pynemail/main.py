import curses
import os

from .imapclient import imap_client, get_mail_from_imap
from .maildirclient import get_mail_from_maildir

from .ui import InboxPage


def mainloop(scr):
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    #mail = get_mail_from_maildir(ROOT)
    with imap_client(scr.getstr().decode()) as client:
        mail = get_mail_from_imap(client)
        #for m in mail:
        #    print(m.filepath, m.unread(), m.date())
        #    #print(dir(m.message()))
        #    #print(m.message().as_string())
        #    print(m.message().keys())
        #    print(m.message()['From'])
        #    print(m.message()['Date'])
        #    #print(m.message().items())
        #    print(m.body())
        page = InboxPage(scr, mail)
        while True:
            scr.clear()
            page.render()

            #scr.move(*cursor)
            page.refresh()
            key = scr.getch()
            #scr.addstr(40, 0, str(key))
            #page.refresh()
            if key == ord('q') or key == ord('Q'):
                break
            elif key == curses.KEY_RESIZE:
                pass  # TODO: Something!
            page.keypress(key)


def main():
    os.environ.setdefault('ESCDELAY', '25')
    curses.wrapper(mainloop)


if __name__ == "__main__":
    main()
