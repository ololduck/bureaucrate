# -*- coding: utf-8 -*-

from mailbox import Maildir, MaildirMessage
from typing import List, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps


class Mailbox(Maildir):
    def __iter__(self):
        for k, v in self.iteritems():
            v.mailbox = self
            v.key = k
            yield v


def init(mailbox_base: str, mailbox_names: List[str]) -> List[Mailbox]:
    from os.path import join
    mailboxes = {}
    for mailbox_name in mailbox_names:
        mailboxes[mailbox_name] = Mailbox(join(mailbox_base, mailbox_name),
                                          factory=Message.message_factory)
    return mailboxes


def condition(f):
    """
    Decorator for conditions, that handles errors, and maybe interrupts filterchain execution
    """
    @wraps(f)
    def try_execute(*args, **kwargs):
        try:
            res, m = f(*args, **kwargs)
            m.condition_results.append(res)
            return m
        except:
            # TODO: return something useful
            pass
    return try_execute


class Message(MaildirMessage):

    @staticmethod
    def message_factory(message):
        return Message(message)

    def __init__(self, *args, **kwargs):
        self.conditions_results = []
        self.mailbox: Optional[Mailbox]
        super().__init__(*args, **kwargs)

    @condition
    def negate(self):
        # type: () -> (bool, Message)
        """
        Changes the result of last condition to the opposite of what it was
        """
        # bool(a) != bool(b) is a x-or
        self.conditions_results[-1] = self.conditions_results[-1] != True
        return True, self

    @condition
    def is_from(self, target: str):
        # type: (str) -> (bool, Message)
        return target in str(self['from']), self

    @condition
    def subject_has(self, subject: str):
        # type: (str) -> (bool, Message)
        return subject in str(self['subject']), self

    @condition
    def older_than(self, timespec):
        # type: (str) -> (bool, Message)
        now = datetime.now()
        if 'd' in timespec:
            d = now - timedelta(days=int(timespec[:-1]))
            if datetime.fromtimestamp(self.get_date()) < d:
                return True, self
        return False, self

    # actions
    def mark_as_read(self):
        # type: () -> Message
        if self.passes_conditions:
            self.add_flag('S')
        return self

    def star(self):
        # type: () -> Message
        if self.passes_conditions:
            self.add_flag('F')
        return self

    def delete(self) -> None:
        """
        Warning! Deletion is final and will break the execution chain!
        :return: None
        """
        if self.passes_conditions:
            self.add_flag('T')
            self.mailbox.remove(self.key)
        return None

    def move_to(self, box: Mailbox):
        # type: (Mailbox) -> Message
        if self.passes_conditions:
            key = box.add(self)
            self.delete()
            return box.get(key)


