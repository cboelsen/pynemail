import getpass
import imaplib

from contextlib import contextmanager
from enum import Enum

from .email import Email, EmailFlag


class ImapFlag(Enum):

    REPLIED = r'\Answered'
    SEEN = r'\Seen'
    FLAGGED = r'\Flagged'
    DELETED = r'\Deleted'
    DRAFT = r'\Draft'
    RECENT = r'\Recent'

MAP_FLAG_TO_IMAP = {
    EmailFlag.REPLIED: ImapFlag.REPLIED,
    EmailFlag.READ: ImapFlag.SEEN,
    EmailFlag.FLAGGED: ImapFlag.FLAGGED,
    EmailFlag.DELETED: ImapFlag.DELETED,
    EmailFlag.DRAFT: ImapFlag.DRAFT,
}


def parse_imap_flags(flagstr):
    parsed_flag_strings = [f.decode() for f in imaplib.ParseFlags(flagstr[0])]
    flags = []
    for flag in ImapFlag:
        if flag.value in parsed_flag_strings:
            flags.append(flag)
    return flags


class ImapEmail(Email):

    flag_enum = ImapFlag
    flag_map = MAP_FLAG_TO_IMAP

    def __init__(self, imapcon, num):
        super().__init__()
        self._num = num
        self._imapcon = imapcon
        self.clear()

    def _get_headers(self):
        _, data = self._imapcon.fetch(self._num, '(RFC822.HEADER)')
        return self.parser.parsebytes(data[0][1])

    def _get_message(self):
        self._flags = None
        _, data = self._imapcon.fetch(self._num, '(RFC822)')
        return self.parser.parsebytes(data[0][1])

    def flags(self):
        if self._flags is None:
            _, flagstr = self._imapcon.fetch(self._num, '(FLAGS)')
            self._flags = parse_imap_flags(flagstr)
        return self._flags

    def set_flag(self, flag, state):
        command = '+FLAGS' if state else '-FLAGS'
        assert flag in MAP_FLAG_TO_IMAP
        imap_flag = MAP_FLAG_TO_IMAP[flag]
        self._imapcon.store(self._num, command, imap_flag.value)


@contextmanager
def imap_client(server, password):
    server, port = server.split(':') if ':' in server else server, imaplib.IMAP4_PORT
    M = imaplib.IMAP4(host=server, port=port)
    M.login(getpass.getuser(), password)
    M.select()
    try:
        yield M
    finally:
        M.close()
        M.logout()


def get_mail_from_imap(client):
    M = client
    _, data = M.search(None, 'ALL')
    mails = [ImapEmail(client, num) for num in data[0].split()]
    return list(reversed(mails))
