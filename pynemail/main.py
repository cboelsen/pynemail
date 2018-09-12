import argparse
import curses
import getpass
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
from .ui.utils import fit_text_to_cols, hidden_cursor

import asyncio
import urwid


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


def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()


class MailItem(urwid.Button):
    button_left = urwid.Text("")
    button_right = urwid.Text("")


class Mailbox(urwid.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def main():
    args = parse_args()

    with ExitStack() as stack:
        if args.maildir:
            maildir = pathlib.Path(args.maildir)
            get_mail = lambda: get_mail_from_maildir(maildir)
            poll_mail_change = lambda fn: poll_maildir(maildir, fn)
            purge_deleted_mail = lambda mail: purge_maildir(maildir, mail)
        elif args.imap:
            client = stack.enter_context(imap_client(args.imap, getpass.getpass()))
            get_mail = lambda: get_mail_from_imap(client)
            poll_mail_change = lambda fn: poll_imap_server(client, fn)
            purge_deleted_mail = lambda mail: purge_imap(client, mail)
        else:
            raise Exception("Argh! How'd I get here!")

        mail = get_mail()
        #page = InboxPage(app.screen, mail)
        #page.resize(curses.LINES, curses.COLS)

        palette = [
            ('bright', 'dark gray', 'light gray', 'bold', '#222', '#ccc'),
            ('streak', '', '', '', 'g50', '#60a'),
            ('inside', '', '', '', 'g38', '#808'),
            ('outside', '', '', '', 'g27', '#a06'),
            ('bg', '', '', '', 'g7', '#d06'),
        ]

        #def update_mail():
        #    mail = get_mail()
        #    page.set_mail(mail)
        mail_widgets = []
        for m in mail:
            from_text = fit_text_to_cols(m.sender(), 30)
            subject_text = fit_text_to_cols(m.subject(), 50)
            text = '{}{}{}'.format(from_text, subject_text, m.date())
            w = urwid.AttrMap(MailItem(text), None, 'bright')
            mail_widgets.append(w)
        #lb = urwid.ListBox(urwid.SimpleFocusListWalker(mail_widgets))
        lb = urwid.ListBox([])
        header = urwid.Pile([urwid.Text('Blah blah blah'), urwid.Divider()])
        f = Mailbox(lb, header=header)
        aioloop = asyncio.get_event_loop()
        evl = urwid.AsyncioEventLoop(loop=aioloop)
        loop = urwid.MainLoop(f, palette, event_loop=evl, unhandled_input=show_or_exit)
        loop.screen.set_terminal_properties(colors=256)
        aioloop.call_later(1, lambda: lb._set_body(urwid.SimpleFocusListWalker(mail_widgets)))
        with hidden_cursor():
            loop.run()

        #app.repeat(30, poll_mail_change, update_mail)
        #app.run(page)
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
