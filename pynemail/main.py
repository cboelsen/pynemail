import argparse
import curses
import os
import pathlib
import time

from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from multiprocessing import Event, Process

from .imapclient import (
    imap_client,
    get_mail_from_imap,
    poll_imap_server,
    purge_imap,
)
from .maildirclient import (
    get_mail_from_maildir,
    poll_maildir,
    purge_maildir,
)

from .ui import App, InboxPage


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


def main():
    args = parse_args()
    os.environ.setdefault('ESCDELAY', '25')
    with App() as app:
        setup_curses(app.screen)

        with ExitStack() as stack:
            if args.maildir:
                maildir = pathlib.Path(args.maildir)
                get_mail = lambda: get_mail_from_maildir(maildir)
                poll_mail_change = lambda fn: poll_maildir(maildir, fn)
                purge_deleted_mail = lambda mail: purge_maildir(maildir, mail)
            elif args.imap:
                client = stack.enter_context(imap_client(args.imap, app.screen.getstr().decode()))
                get_mail = lambda: get_mail_from_imap(client)
                poll_mail_change = lambda fn: poll_imap_server(client, fn)
                purge_deleted_mail = lambda mail: purge_imap(client, mail)
            else:
                raise Exception("Argh! How'd I get here!")

            mail = get_mail()
            page = InboxPage(app.screen, mail)
            page.resize(curses.LINES, curses.COLS)

            def update_mail():
                mail = get_mail()
                page.set_mail(mail)

            app.repeat(30, poll_mail_change, update_mail)
            app.run(page)
            purge_deleted_mail(mail)
    #with ExitStack() as stack:
    #    import getpass
    #    client = stack.enter_context(imap_client(args.imap, getpass.getpass()))
    #    mail = get_mail_from_imap(client)
    #    import pdb
    #    pdb.set_trace()
    #    print(mail)


if __name__ == "__main__":
    main()
