from email.parser import BytesParser
from email.policy import default as default_policy
from enum import Enum


class EmailFlag(Enum):
    REPLIED = 0
    READ = 1
    FLAGGED = 2
    DELETED = 3
    DRAFT = 4


class Email:

    flag_enum = None
    flag_map = None
    parser = BytesParser(policy=default_policy)

    def __init__(self):
        self.clear()

    def _get_message(self):
        raise NotImplementedError('Email.message()')

    def unread(self):
        if self._unread is None:
            self._unread = self.flag_enum.SEEN not in self.flags()
        return self._unread

    def important(self):
        if self._important is None:
            self._important = self.flag_enum.FLAGGED in self.flags()
        return self._important

    def replied(self):
        if self._replied is None:
            self._replied = self.flag_enum.REPLIED in self.flags()
        return self._replied

    def deleted(self):
        if self._deleted is None:
            self._deleted = self.flag_enum.DELETED in self.flags()
        return self._deleted

    def draft(self):
        if self._draft is None:
            self._draft = self.flag_enum.DRAFT in self.flags()
        return self._draft

    def message(self):
        if self._message is None:
            self._message = self._get_message()
        return self._message

    def headers(self):
        if self._headers is None:
            self._headers = self._get_headers()
        return self._headers

    def body(self):
        if self._body is None:
            if self.unread():
                self.set_flag(EmailFlag.READ, True)
            self._body = self.message().get_body(preferencelist=('plain', )).get_content()
        return self._body

    def sender(self):
        if self._from is None:
            f = self.headers()['From']
            if ' ' in f:
                f = ' '.join(f.split(' ')[:-1]).strip()
            if f[0] == '"' and f[-1] == '"':
                f = f[1:-1]
            self._from = f
        return self._from

    def to(self):
        return self.headers()['To']

    def date(self):
        return self.headers()['Date'][:-5]

    def subject(self):
        return self.headers()['Subject']

    def flags(self):
        """Return the flags set for this email.

        :return: A list of flags.
        :rtype: list[EmailFlag]
        """
        raise NotImplementedError('Email.flags()')

    def set_flag(self, flag, state):
        """Set or unset the given flag, based on the provided state.

        :param EmailFlag flag: The flag to manipulate.
        :param bool state: True to set the flag, False to unset the flag.
        """
        raise NotImplementedError('Email.set_flag()')

    def clear(self):
        """Clear all cached state to force the lazy initialisers to reload."""
        self.clear_flags()
        self._date = None
        self._headers = None
        self._message = None
        self._body = None
        self._from = None
        self._flags = None

    def clear_flags(self):
        """Clear all cached flags to force the lazy initialisers to reload."""
        self._unread = None
        self._important = None
        self._replied = None
        self._deleted = None
        self._draft = None
