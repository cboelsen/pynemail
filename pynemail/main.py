import argparse
import curses
import os
import pathlib
import time

from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from multiprocessing import Event, Process

from .imapclient import imap_client, get_mail_from_imap, poll_imap_server
from .maildirclient import get_mail_from_maildir, poll_maildir

from .ui import InboxPage


class CheckImapServerAction:

    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None):
        self.option_strings = option_strings
        self.dest = dest
        self.nargs = nargs
        self.const = const
        self.default = default
        self.type = type
        self.choices = choices
        self.required = required
        self.help = help
        self.metavar = metavar

    def __call__(self, parser, namespace, values, option_string=None):
        assert isinstance(values, str)
        if values.count(':') > 1:
            parser.error('The provided IMAP server is not valid: {}'.format(values))
        else:
            setattr(namespace, self.dest, values)


def parse_args():
    parser = argparse.ArgumentParser(description='')
    mailtype = parser.add_mutually_exclusive_group(required=True)
    mailtype.add_argument('--maildir', metavar='DIR',
                          help='The location of the maildir')
    mailtype.add_argument('--imap', action=CheckImapServerAction, metavar='SERVER',
                          help='The address (and/or port) of the IMAP server')
    args = parser.parse_args()
    return args


def setup_curses(scr):
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.curs_set(0)


def mainloop(scr, args):
    setup_curses(scr)

    new_mail = Event()

    with ExitStack() as stack:
        if args.maildir:
            maildir = pathlib.Path(args.maildir)
            get_mail = lambda: get_mail_from_maildir(maildir)
            background_fn = lambda: poll_maildir(maildir, new_mail)
        elif args.imap:
            client = stack.enter_context(imap_client(args.imap, scr.getstr().decode()))
            get_mail = lambda: get_mail_from_imap(client)
            background_fn = lambda: poll_imap_server(client, new_mail)
        else:
            raise Exception("Argh! How'd I get here!")

        scr.nodelay(True)
        mail = get_mail()
        page = InboxPage(scr, mail)

        #background_process = Process(target=background_fn, daemon=True)
        #background_process.start()

        while True:
            page.render()

            page.refresh()
            key = -1
            while key == -1:
                key = scr.getch()
                time.sleep(0.02)
                #if new_mail.wait(0.02):
                #    mail = get_mail()
                #    page.set_mail(mail)
                #    scr.clear()
                #    page.render()
                #    page.refresh()
                    #scr.addstr(40, 0, str(client.recent()))
                    #page.refresh()
            #scr.addstr(40, 0, str(key))
            #page.refresh()
            if key == ord('q') or key == ord('Q'):
                break
            elif key == curses.KEY_RESIZE:
                pass  # TODO: Something!
            page.keypress(key)


def main():
    args = parse_args()
    os.environ.setdefault('ESCDELAY', '25')
    curses.wrapper(mainloop, args)


if __name__ == "__main__":
    main()
