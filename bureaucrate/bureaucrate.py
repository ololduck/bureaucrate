# -*- coding: utf-8 -*-

import datetime
from functools import wraps
from mailbox import Maildir, MaildirMessage
from os import listdir
from os.path import join, isdir
from typing import List, Optional, Dict

from .utils import parse_timespec


class Mailbox(Maildir):
    def __iter__(self):
        for k, v in self.iteritems():
            v.mailbox = self
            v.key = k
            yield v

base_path = str
mailboxes = Dict[Mailbox]


def get_mailbox(mb_id: str) -> Mailbox:
    """
    gets or creates a Mailbox representation of the directory at base_path + mb_id
    :param mb_id:
    :return:
    """
    global mailboxes
    if mb_id not in mailboxes:
        mb = Mailbox(join(base_path, mb_id), factory=Message.message_factory)
        mailboxes[mb_id] = mb
    else:
        mb = mailboxes[mb_id]
    return mb


def init(mailbox_base: str, mailbox_names: List[str]) -> List[Mailbox]:
    global mailboxes, base_path
    base_path = mailbox_base
    if not mailbox_names:
        mailbox_names = [e for e in listdir(mailbox_base) if isdir(e)]
    mailboxes = {}
    for mailbox_name in mailbox_names:
        mailboxes[mailbox_name] = Mailbox(join(mailbox_base, mailbox_name),
                                          factory=Message.message_factory)
    return mailboxes


def condition(f):
    """
    Decorator for conditions
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


def action(f):
    """
    decorator for actions.
    """
    @wraps(f)
    def decorate(message, *args, **kwargs):
        if message.conditions_results.count(True) == len(message.conditions_results):
            return f(message, *args, **kwargs)
        return None
    return decorate


class Message(MaildirMessage):

    @staticmethod
    def message_factory(message):
        return Message(message)

    def __init__(self, *args, **kwargs):
        self.conditions_results = []
        self.mailbox = Optional[Mailbox]
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
    def starred(self):
        return 'F' in self.get_flags(), self

    @condition
    def read(self):
        return 'S' in self.get_flags(), self

    @condition
    def subject_has(self, subject: str):
        # type: (str) -> (bool, Message)
        return subject in str(self['subject']), self

    @condition
    def older_than(self, timespec: str):
        # type: (str) -> (bool, Message)
        now = datetime.now()
        if 'd' in timespec:
            d = now - parse_timespec(timespec)
            if datetime.fromtimestamp(self.get_date()) < d:
                return True, self
        return False, self

    @condition
    def is_list(self):
        return "List-Id" in self.keys(), self

    # actions
    @action
    def mark_as_read(self):
        # type: () -> Message
        self.add_flag('S')
        return self

    @action
    def star(self):
        # type: () -> Message
        self.add_flag('F')
        return self

    @action
    def delete(self) -> None:
        """
        Warning! Deletion is final and will break the execution chain!
        :return: None
        """
        self.add_flag('T')
        self.mailbox.remove(self.key)
        return None

    @action
    def move_to(self, box: str):
        # type: (Mailbox) -> Message
        box = get_mailbox(box)
        key = box.add(self)
        self.delete()
        return box.get(key)

    def get_list(self):
        return str(self['list-id']).strip('<').strip('>')


