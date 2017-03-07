# -*- coding: utf-8 -*-

from mailbox import Maildir, MaildirMessage
from typing import List


class Mailbox(Maildir):
    pass


mailboxes: List[Mailbox]
mailboxes_name: str
mailboxes_base: str


def init():
    """
    Initialises the global vars
    """
    global mailboxes, mailboxes_name, mailboxes_base


class Message(MaildirMessage):
    def __init__(self, **kwargs):
        self.passes_conditions = True
        super().__init__(**kwargs)

    # conditions
    def is_from(self, target: str):
        # type: (str) -> Message
        if self.passes_conditions and target in self['from']:
            return self
        self.passes_conditions = False
        return self

    def subject_has(self, subject:str):
        # type: (str) -> Message
        if self.passes_conditions and subject in self['Subject']:
            return self
        self.passes_conditions = False
        return self

    def older_than(self, timespec):
        # type: (str) -> Message
        if self.passes_conditions:
            raise NotImplementedError()
        self.passes_conditions = False
        return self

    # actions
    def mark_as_read(self):
        # type: () -> Message
        if self.passes_conditions:
            self.add_flag('S')
        return self

    def delete(self):
        if self.passes_conditions:
            self.add_flag('T')

    def move_to(self, box: str):
        # type: (str) -> Message
        # TODO: add mailbox creation if it doesn't exist
        global mailboxes
        if self.passes_conditions:
            key = mailboxes[box].add(self)
            # Now, let's mark ourselves for deletion
            self.delete()
            return mailboxes[box].get(key)
        raise RuntimeError('could not move message %s to box %s',
                           self, mailboxes[box])


