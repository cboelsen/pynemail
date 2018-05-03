import os
import pathlib

from enum import Enum

from .email import Email, EmailFlag


# TODO: Make this configurable!
ROOT = pathlib.Path(os.environ['HOME']) / '.maildir'


class MaildirFlag(Enum):

    FORWARDED = 'P'
    REPLIED = 'R'
    SEEN = 'S'
    DELETED = 'T'
    DRAFT = 'D'
    FLAGGED = 'F'


MAP_FLAG_TO_MAILDIR = {
    EmailFlag.REPLIED: MaildirFlag.REPLIED,
    EmailFlag.READ: MaildirFlag.SEEN,
    EmailFlag.FLAGGED: MaildirFlag.FLAGGED,
    EmailFlag.DELETED: MaildirFlag.DELETED,
    EmailFlag.DRAFT: MaildirFlag.DRAFT,
}


class UnknownMaildirFlag(Exception):
    pass


def parse_maildir_flags(filepath):
    flag_string = filepath.name.split(':')[1]
    flag_type, flag_chars = flag_string.split(',')
    if int(flag_type) != 2:
        raise UnknownMaildirFlag(flag_type)
    flags = []
    for flag in MaildirFlag:
        if flag.value in flag_chars:
            flags.append(flag)
    return flags


class MaildirEmail(Email):

    flag_enum = MaildirFlag
    flag_map = MAP_FLAG_TO_MAILDIR

    def __init__(self, filepath, is_new):
        super().__init__()
        self.filepath = filepath
        # TODO: Argh! Do I still want to use this?!?!?!
        self.is_new = is_new
        self.clear()

    def __lt__(self, other):
        assert isinstance(other, self.__class__)
        return self.mtime() < other.mtime()

    def __hash__(self):
        return hash(self.filepath)

    def _get_headers(self):
        return self.message()

    def _get_message(self):
        with self.filepath.open('rb') as fp:
            return self.parser.parse(fp)

    def flags(self):
        if self._flags is None:
            self._flags = parse_maildir_flags(self.filepath)
        return self._flags

    def mtime(self):
        if self._mtime is None:
            self._mtime = self.filepath.stat().st_mtime
        return self._mtime

    def clear(self):
        super().clear()
        self._mtime = None


def get_mail_from_maildir(maildir):
    newmail = [MaildirEmail(e, True) for e in (maildir / 'new').glob('*')]
    curmail = [MaildirEmail(e, False) for e in (maildir / 'cur').glob('*')]
    return sorted(newmail + curmail, reverse=True)
