import os
import pathlib

from enum import Enum
from typing import List, Dict

from .email import Email, EmailFlag


MAP_FLAG_TO_MAILDIR = {
    EmailFlag.ANSWERED: 'R',
    EmailFlag.SEEN: 'S',
    EmailFlag.FLAGGED: 'F',
    EmailFlag.DELETED: 'T',
    EmailFlag.DRAFT: 'D',
}   # type: Dict[EmailFlag, str]


class UnknownMaildirFlagsType(Exception):
    pass


def parse_maildir_flags(filepath: pathlib.Path) -> List[EmailFlag]:
    flag_string = filepath.name.split(':')[1]
    flag_type, flag_chars = flag_string.split(',')
    if int(flag_type) != 2:
        raise UnknownMaildirFlagsType(flag_type)
    flags = []
    for flag in EmailFlag:
        if MAP_FLAG_TO_MAILDIR[flag] in flag_chars:
            flags.append(flag)
    return flags


def update_maildir_flags(filepath: pathlib.Path, flags: List[EmailFlag]) -> pathlib.Path:
    keep_name, flag_string = filepath.name.split(':')
    flag_type, flag_chars = flag_string.split(',')
    if int(flag_type) != 2:
        raise UnknownMaildirFlagsType(flag_type)
    newflag_string = ''.join(sorted([MAP_FLAG_TO_MAILDIR[f] for f in flags]))
    newname = '{}:{},{}'.format(keep_name, flag_type, newflag_string)
    newpath = filepath.parent / newname
    filepath.rename(newpath)
    return newpath


class MaildirEmail(Email):

    def __init__(self, filepath: pathlib.Path, is_new: bool) -> None:
        super().__init__()
        self.filepath = filepath
        # TODO: Argh! Do I still want to use this?!?!?!
        self.is_new = is_new
        self._mtime = 0.0  # type: float
        self.clear()

    def __lt__(self, other: 'MaildirEmail') -> bool:
        assert isinstance(other, self.__class__)
        return self.mtime() < other.mtime()

    def __hash__(self) -> int:
        return hash(self.filepath)

    def _get_headers(self):
        return self.message()

    def _get_message(self):
        with self.filepath.open('rb') as fp:
            return self.parser.parse(fp)

    def _get_flags(self):
        return parse_maildir_flags(self.filepath)

    def set_flag(self, flag, state):
        if state and flag not in self._flags:
            self._flags.append(flag)
            self.filepath = update_maildir_flags(self.filepath, self._flags)
            self.clear_flags()
        elif flag in self._flags:
            self._flags.remove(flag)
            self.filepath = update_maildir_flags(self.filepath, self._flags)
            self.clear_flags()

    def mtime(self) -> float:
        if self._mtime == 0.0:
            self._mtime = self.filepath.stat().st_mtime
        return self._mtime

    def clear(self):
        super().clear()
        self._mtime = 0.0


def poll_maildir(maildir: pathlib.Path, update_mail):
    pass


def purge_maildir(maildir: pathlib.Path, mail: List[MaildirEmail]) -> None:
    for email in mail:
        if email.deleted():
            email.filepath.unlink()


def get_mail_from_maildir(maildir: pathlib.Path) -> List[MaildirEmail]:
    newmail = [MaildirEmail(e, True) for e in (maildir / 'new').glob('*')]
    curmail = [MaildirEmail(e, False) for e in (maildir / 'cur').glob('*')]
    return sorted(newmail + curmail, reverse=True)
