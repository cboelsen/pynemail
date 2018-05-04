import getpass
import imaplib

from contextlib import contextmanager
from enum import Enum
from typing import List, Dict, Generator

from .email import Email, EmailFlag


MAP_FLAG_TO_IMAP = {
    EmailFlag.ANSWERED: r'Answered',
    EmailFlag.SEEN: r'\Seen',
    EmailFlag.FLAGGED: r'\Flagged',
    EmailFlag.DELETED: r'\Deleted',
    EmailFlag.DRAFT: r'\Draft',
}  # type: Dict[EmailFlag, str]


def parse_imap_flags(flagstr: List[bytes]) -> List[EmailFlag]:
    parsed_flag_strings = [f.decode() for f in imaplib.ParseFlags(flagstr[0])]
    flags = []
    for flag in EmailFlag:
        if MAP_FLAG_TO_IMAP[flag] in parsed_flag_strings:
            flags.append(flag)
    return flags


class ImapEmail(Email):

    def __init__(self, imapcon: imaplib.IMAP4, num: int) -> None:
        super().__init__()
        self._num = num
        self._imapcon = imapcon
        self.clear()

    def _get_headers(self):
        _, data = self._imapcon.fetch(self._num, '(RFC822.HEADER)')
        return self.parser.parsebytes(data[0][1])

    def _get_message(self):
        _, data = self._imapcon.fetch(self._num, '(RFC822)')
        return self.parser.parsebytes(data[0][1])

    def _get_flags(self):
        _, flagstr = self._imapcon.fetch(self._num, '(FLAGS)')
        return parse_imap_flags(flagstr)

    def set_flag(self, flag: EmailFlag, state: bool) -> None:
        command = '+FLAGS' if state else '-FLAGS'
        assert flag in MAP_FLAG_TO_IMAP
        imap_flag = MAP_FLAG_TO_IMAP[flag]
        self._imapcon.store(self._num, command, imap_flag)
        self.clear_flags()


@contextmanager
def imap_client(server: str, password: str) -> Generator:
    server, port = server.split(':') if ':' in server else server, imaplib.IMAP4_PORT
    M = imaplib.IMAP4(host=server, port=port)
    M.login(getpass.getuser(), password)
    M.select()
    try:
        yield M
    finally:
        M.close()
        M.logout()


def get_mail_from_imap(client: imaplib.IMAP4) -> List[ImapEmail]:
    _, data = client.search("", 'ALL')
    mails = [ImapEmail(client, num) for num in data[0].split()]
    return list(reversed(mails))
