from email.message import EmailMessage
from email.parser import BytesParser
from email.policy import default as default_policy
from enum import Enum
from typing import List, Optional


class EmailFlag(Enum):
    """A set of standard flags according to RFC3501, ignoring RECENT."""

    ANSWERED = 'R'
    SEEN = 'S'
    FLAGGED = 'I'
    DELETED = 'X'
    DRAFT = 'D'


class Email:
    """A cached copy of a single email."""

    parser = BytesParser(policy=default_policy)

    def __init__(self):
        self._date = None
        self._headers = None
        self._message = None
        self._body = None
        self._from = None
        self._flags = None
        self._unread = None
        self._important = None
        self._replied = None
        self._deleted = None
        self._draft = None

    def _get_flags(self) -> EmailMessage:
        raise NotImplementedError('Email._get_flags()')

    def _get_headers(self) -> EmailMessage:
        raise NotImplementedError('Email._get_headers()')

    def _get_message(self) -> EmailMessage:
        raise NotImplementedError('Email._get_message()')

    def unread(self) -> bool:
        if self._unread is None:
            self._unread = EmailFlag.SEEN not in self.flags()
        return self._unread

    def important(self) -> bool:
        if self._important is None:
            self._important = EmailFlag.FLAGGED in self.flags()
        return self._important

    def replied(self) -> bool:
        if self._replied is None:
            self._replied = EmailFlag.ANSWERED in self.flags()
        return self._replied

    def deleted(self) -> bool:
        if self._deleted is None:
            self._deleted = EmailFlag.DELETED in self.flags()
        return self._deleted

    def draft(self) -> bool:
        if self._draft is None:
            self._draft = EmailFlag.DRAFT in self.flags()
        return self._draft

    def headers(self) -> EmailMessage:
        if self._headers is None:
            self._headers = self._get_headers()
        return self._headers

    def message(self) -> EmailMessage:
        if self._message is None:
            self._message = self._get_message()
        return self._message

    def body(self) -> str:
        if self._body is None:
            if self.unread():
                self.set_flag(EmailFlag.SEEN, True)
            body = self.message().get_body(preferencelist=('plain', ))
            if body is None:
                self._body = " PynEmail Error: Unable to read email body!"
            else:
                self._body = body.get_content()
        return self._body

    def sender(self) -> str:
        if self._from is None:
            fro = self.headers()['From']
            if ' ' in fro:
                fro = ' '.join(fro.split(' ')[:-1]).strip()
            if fro[0] == '"' and fro[-1] == '"':
                fro = fro[1:-1]
            self._from = fro
        return self._from

    def to(self) -> str:
        return self.headers()['To']

    def date(self) -> str:
        return self.headers()['Date'][:-5]

    def subject(self) -> str:
        return self.headers()['Subject']

    def flags(self) -> List[EmailFlag]:
        """Return the flags set for this email.

        :return: A list of flags.
        :rtype: list[EmailFlag]
        """
        if self._flags is None:
            self._flags = self._get_flags()
        return self._flags

    def set_flag(self, flag: EmailFlag, state: bool) -> None:
        """Set or unset the given flag, based on the provided state.

        :param EmailFlag flag: The flag to manipulate.
        :param bool state: True to set the flag, False to unset the flag.
        """
        raise NotImplementedError('Email.set_flag()')

    def clear(self) -> None:
        """Clear all cached state to force the lazy initialisers to reload."""
        self.clear_flags()
        self._date = None
        self._headers = None
        self._message = None
        self._body = None
        self._from = None

    def clear_flags(self) -> None:
        """Clear all cached flags to force the lazy initialisers to reload."""
        self._flags = None
        self._unread = None
        self._important = None
        self._replied = None
        self._deleted = None
        self._draft = None
