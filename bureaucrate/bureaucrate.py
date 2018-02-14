# -*- coding: utf-8 -*-

import re
from datetime import datetime
from email.header import decode_header
from functools import wraps
from mailbox import Maildir, MaildirMessage
from os import listdir
from os.path import join, expanduser
from subprocess import run, PIPE
from typing import List, Optional, Dict

from chardet import detect
from dateutil.parser import parse as dateparse
from logging import getLogger, basicConfig

from .utils import parse_timespec


logger = getLogger(__name__)
FORMAT = "%(filename)s:%(lineno)3s - %(funcName)15s - %(levelname)s: %(" \
         "message)s"
basicConfig(format=FORMAT)


class ConditionError(Exception):
    pass


class Mailbox(Maildir):
    def __iter__(self):
        for k, v in self.iteritems():
            v.mailbox = self
            v.key = k
            yield v


base_path = str
mailboxes = Dict[str, Mailbox]


def get_mailbox(mb_id: str) -> Mailbox:
    """
    gets or creates a Mailbox representation of the directory at
    base_path + mb_id
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


def init(mailbox_base: str, mailbox_names: List[str]=[]) -> Dict[str, Mailbox]:
    logger.info('Initializing mailboxes at %s', mailbox_base)
    global mailboxes, base_path
    base_path = expanduser(mailbox_base)
    if not mailbox_names:
        mailbox_names = [e for e in listdir(base_path)]
    mailboxes = {}
    for mailbox_name in mailbox_names:
        mailboxes[mailbox_name] = Mailbox(join(mailbox_base, mailbox_name),
                                          factory=Message.message_factory)
        logger.debug('mailbox found in %s: %s', mailbox_base, mailbox_name)
    return mailboxes


def condition(f):
    """
    Decorator for conditions
    """

    @wraps(f)
    def try_execute(*args, **kwargs):
        try:
            res, m = f(*args, **kwargs)
            m.conditions_results.append(res)
            return m
        except Exception as e:
            raise ConditionError(e)
    return try_execute


def action(f):
    """
    decorator for actions. Reinitialises the conditions_result array after action execution
    """

    @wraps(f)
    def decorate(message, *args, **kwargs):
        r = None
        if message.conditions_results.count(True) == \
            len(message.conditions_results):
            r = f(message, *args, **kwargs)
        return r or message

    return decorate


class Message(MaildirMessage):
    """
    Represents a mail message, and its associated conditions and actions
    """

    def __getitem__(self, name):
        "Let's convert headers to str"
        message = []
        if name not in self:
            logger.debug("name not found: %s", name)
            return ""
        for t in decode_header(super().__getitem__(name)):
            logger.debug("t: %s", t)
            if type(t[0]) is bytes:
                if t[1] == 'unknown-8bit':
                    logger.info('found unknown charset: %s', t)
                    try:
                        supposition = detect(t[0])
                        logger.debug('trying to recover as %s', supposition)
                        message.append(t[0].decode(supposition['encoding']))
                    except:
                        logger.error('Failed to recover "%s" as %s', t[0], supposition)
                        raise ValueError('Incorrect encoding for Message: %s' %
                                         super().__getitem__('subject'))
                else:
                    message.append(t[0].decode(t[1] or 'ASCII'))
            if type(t[0]) is str:
                message.append(t[0])
        return ''.join(message)

    @staticmethod
    def message_factory(message):
        m = Message(message)
        logger.debug(m['Date'])
        d = dateparse(m['Date'])
        m.set_date(d.timestamp())
        return m

    def __init__(self, *args, **kwargs):
        self.conditions_results = []
        self.mailbox = Optional[Mailbox]
        super().__init__(*args, **kwargs)

    def exec_rule(self, rule):
        for cond in rule['conditions']:
            logger.debug("eval cond: %s", cond)
            if len(cond) > 1:
                getattr(self, cond[0])(*cond[1:])
            else:
                getattr(self, cond[0])()
        for act in rule['actions']:
            logger.debug("eval action: %s", act)
            if len(act) > 1:
                getattr(self, act[0])(*act[1:])
            else:
                getattr(self, act[0])()

    def exec_rules(self, rules: List):
        for rule in rules:
            self.exec_rule(rule)
            self.conditions_results = []

    def get_list(self) -> str:
        s = str(self.get('list-id', ''))
        return s[s.find('<'):s.find('>')].strip('<').strip('>')

    @condition
    def negate(self):
        # type: () -> (bool, Message)
        """
        Changes the result of last condition to the opposite of what it was
        """
        self.conditions_results[-1] = not self.conditions_results[-1]
        return True, self

    @condition
    def is_from(self, target: str):
        """
        Returns True if target is in From: header

        >>> m = Message()
        >>> m['From'] = "Sample <example@test.org>"
        >>> _ = m.is_from('Sample')
        >>> m.conditions_results[-1]
        True
        >>> _ = m.is_from('example')
        >>> m.conditions_results[-1]
        True
        >>> _ = m.is_from('@test.org')
        >>> m.conditions_results[-1]
        True
        >>> _ = m.is_from('Paul')
        >>> m.conditions_results[-1]
        False
        """
        # type: (str) -> (bool, Message)
        return target in self['from'], self

    @condition
    def starred(self):
        """
        Returns True if message is flagged or 'starred'

        >>> m = Message()
        >>> _ = m.starred()
        >>> m.conditions_results[-1]
        False
        >>> m.set_flags('F')
        >>> _ = m.starred()
        >>> m.conditions_results[-1]
        True
        """
        # type: () -> (bool, Message)
        return 'F' in self.get_flags(), self

    @condition
    def read(self):
        """
        Returns True if message is seen or 'read'

        >>> m = Message()
        >>> _ = m.read()
        >>> m.conditions_results[-1]
        False
        >>> m.conditions_results = [] # reset conditional action exec
        >>> m.conditions_results
        []
        >>> _ = m.mark_as_read()
        >>> 'S' in m.get_flags()
        True
        >>> _ = m.read()
        >>> m.conditions_results[-1]
        True
        """
        # type: () -> (bool, Message)
        return 'S' in self.get_flags(), self

    @condition
    def subject_has(self, subject: str):
        """
        Returns True if target is in Subject: header

        >>> m = Message()
        >>> m['Subject'] = "Hi there!"
        >>> _ = m.subject_has('Hi')
        >>> m.conditions_results[-1]
        True
        >>> _ = m.subject_has('there')
        >>> m.conditions_results[-1]
        True
        >>> _ = m.subject_has('Hello')
        >>> m.conditions_results[-1]
        False
        """
        # type: (str) -> (bool, Message)
        return subject in self['subject'], self

    @condition
    def older_than(self, timespec: str):
        """
        Return True if message is older than 'timespec'.

        'timespec' is a simplistic expression of time span, in the form of '\d+[YMDhms]( (\d+[YMDhms]))*'
        """
        # type: (str) -> (bool, Message)
        now = datetime.now()
        d = now + parse_timespec(timespec)
        if datetime.fromtimestamp(self.get_date()) < d:
            return True, self
        return False, self

    @condition
    def is_list(self):
        """
        Returns True if the message is destined to a list, and if the corresponding List-Id: header is set
        """
        # type: () -> (bool, Message)
        return "List-Id" in self.keys(), self

    @condition
    def list_is(self, list: str):
        "Returns True if substring 'list' can be found in header List-Id"
        # type: (str) -> (bool, Message)
        if self.get_list():
            return list in self.get_list(), self
        return False, self

    @condition
    def has_replied(self):
        """
        Returns True if the message has been replied to
        :return:
        """
        # type: () -> (bool, Message)
        return 'R' in self.get_flags(), self

    @condition
    def is_spam(self):
        """
        :return: True if has a Spam header
        """
        if 'X-Spam' in self:
            if re.match(r'[Yy]es|[Tt]rue', self['X-Spam']):
                return True, self
        return False, self

    # actions
    @action
    def mark_as_read(self):
        """
        >>> m = Message()
        >>> 'S' in m.get_flags()
        False
        >>> _ = m.mark_as_read()
        >>> 'S' in m.get_flags()
        True

        :return:
        """
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

    @action
    def copy(self, box: str):
        # type: (Mailbox) -> Message
        box = get_mailbox(box)
        key = box.add(self)
        return box.get(key)

    @action
    def archive(self, archive_format='Archives.%Y'):
        dt = datetime.fromtimestamp(self.get_date())
        return self.move_to(dt.strftime(archive_format))

    @action
    def forward(self, command, mto, mfrom=None):
        m = Message()
        m['From'] = mfrom or self['to']
        m['To'] = mto
        m['Subject'] = "Fwd: " + self['subject']
        m.set_payload(self.get_payload())
        run(command + " " + m['To'],
            stdout=PIPE, input=m.as_string().encode('utf-8'),
            shell=True, check=True)
        return self
