from datetime import timedelta
import re
from shlex import split


def parse_timespec(timespec: str) -> timedelta:
    """
    returns a negative timedelta corresponding to the given timespec
    :param timespec: a space-delimited string of time info. see examples
    :return:
    """
    days = 0
    seconds = 0
    for e in timespec.split():
        if e[-1:] == 'd':
            days -= int(e[:-1])
        if e[-1:] == 'M':
            days -= int(e[:-1]) * 30
        if e[-1:] == 'y':
            days -= int(e[:-1]) * 365
        if e[-1:] == 'h':
            seconds -= int(e[:-1]) * 3600
        if e[-1:] == 'm':
            seconds -= int(e[:-1]) * 60
        if e[-1:] == 's':
            seconds -= int(e[:-1])
    return timedelta(days=days, seconds=seconds)


class InvalidConfigurationError(RuntimeError):
    pass


class Config(object):
    """
    Parses a config file in a special format
    """

    class Context(object):
        def __init__(self):
            self.glob = True
            self.account = None
            self.mailbox = None

    def __init__(self):
        self.config = dict()

    def get_accounts(self):
        return [k for k in self.config.keys()
                if type(self.config[k]) == dict]

    def get_mailboxes(self, account):
        return [k for k in self.config[account].keys()
                if type(self.config[account][k]) == dict]

    def parse(self, path: str):
        ctxt = Config.Context()
        with open(path) as f:
            for line in f.readlines():
                self.parse_line(line, ctxt)

    def parse_line(self, line: str, context: Context):
        """
        >>> c = Config()
        >>> c.parse_line("# terte  ", Config.Context())
        >>> c.parse_line('    # dfgj', Config.Context())
        >>> ctx = Config.Context()
        >>> ctx.glob
        True
        >>> ctx.account
        >>> ctx.mailbox
        >>> c.parse_line("testmb {", ctx)
        >>> ctx.glob
        False
        >>> ctx.account
        'testmb'
        >>> ctx.mailbox
        >>> c.parse_line("refresh = 1", ctx)
        >>> c.config['testmb']["refresh"]
        '1'
        >>> c.parse_line(' }  ', ctx)
        >>> ctx.account
        >>> ctx.glob
        True


        :param line:
        :param context:
        :return:
        """
        if line.strip().startswith('#'):
            # Then it is a comment, we ignore it
            return
        match = re.match('^ *(.*) \{$', line)
        if match:
            if context.glob:
                if context.account is not None or context.mailbox is not None:
                    raise InvalidConfigurationError('error near %s' % line)
                context.glob = False
                context.account = match.group(1)
                self.config[context.account] = {}
                return
            if context.account:
                if context.glob:
                    raise InvalidConfigurationError('error near %s' % line)
                context.mailbox = match.group(1)
                self.config[context.account][context.mailbox] = {}
                self.config[context.account][context.mailbox]['rules'] = []
                return
        match = re.match('^ *(?P<key>.*) = (?P<value>.*)$', line)
        if match:
            key, value = match.group('key'), match.group('value')
            if context.glob:
                self.config[key] = value
            elif context.account and not context.mailbox:
                self.config[context.account][key] = value
            else:
                self.config[context.account][context.mailbox][key] = value
        if line.strip().startswith('if '):
            self.config[context.account][context.mailbox]['rules'].append(
                Config.parse_rule(line))
        if line.strip().startswith('}'):
            if context.mailbox:
                context.mailbox = None
                return
            if context.account:
                context.account = None
                context.glob = True
                return
            return InvalidConfigurationError('got } in an global context')

    def get(self, key, default=None, mb=None, account=None):
        """
        >>> conf = '''a = 1
        ... c = 1
        ... ta1 {
        ...   a = 2
        ...   b = 1
        ...   tmb1 {
        ...     b = 2
        ...     c = 2
        ...     d = 1
        ...   }
        ... }'''
        >>> c = Config()
        >>> ctx = Config.Context()
        >>> for line in conf.splitlines():
        ...     c.parse_line(line, ctx)
        >>> c.get('a', default='test', mb='tmb1', account='ta1')
        '2'
        >>> c.get('b', default='test', mb='tmb1', account='ta1')
        '2'
        >>> c.get('c', default='test', mb='tmb1', account='ta1')
        '2'
        >>> c.get('d', default='test', mb='tmb1', account='ta1')
        '1'
        >>> c.get('a', default='test', account='ta1')
        '2'
        >>> c.get('b', default='test', account='ta1')
        '1'
        >>> c.get('c', default='test', account='ta1')
        '1'
        >>> c.get('d', default='test', account='ta1')
        'test'
        >>> c.get('a', default='test', account='ta1')
        '2'
        >>> c.get('b', default='test', account='ta1')
        '1'
        >>> c.get('c', default='test', account='ta1')
        '1'
        >>> c.get('d', default='test', account='ta1')
        'test'
        >>> c.get('a', default='test')
        '1'
        >>> c.get('b', default='test')
        'test'
        >>> c.get('c', default='test')
        '1'
        >>> c.get('d', default='test')
        'test'

        :param key: the key to fetch
        :param default: a default value to return if the key is not found
        :param mb: name of the mailbox
        :param account: name of the account
        :return: something
        """
        if account:
            if mb:
                if key in self.config[account][mb].keys():
                    return self.config[account][mb][key]
                if key in self.config[account].keys():
                    return self.config[account][key]
                if key in self.config.keys():
                    return self.config[key]
            if key in self.config[account].keys():
                return self.config[account][key]
            if key in self.config.keys():
                return self.config[key]
        if key in self.config.keys():
            return self.config[key]
        return default

    @classmethod
    def parse_rule(cls, line: str) -> dict:
        """
        parses a rule under the form of

            if is_from 'sample@test.net' and read then archive

        >>> Config.parse_rule("read then archive")
        {'conditions': [['read']], 'actions': [['archive']]}
        >>> Config.parse_rule("if is_from sample@test.net and read then archive")
        {'conditions': [['is_from', 'sample@test.net'], ['read']], 'actions': [['archive']]}
        >>> Config.parse_rule("if is_from sample@test.net and read then unstar and archive")
        {'conditions': [['is_from', 'sample@test.net'], ['read']], 'actions': [['unstar'], ['archive']]}
        >>> Config.parse_rule("if is_from 'Hallo leute' then star")
        {'conditions': [['is_from', 'Hallo leute']], 'actions': [['star']]}

        :param line:
        :return: a dict representing the rule
        """
        if line.strip().startswith('if '):
            line = line.strip()[3:]
        conditions, actions = line.split('then')
        conditions = conditions.split('and')
        actions = actions.split('and')
        rule = dict()
        rule['conditions'] = []
        rule['actions'] = []
        for element in conditions:
            rule['conditions'].append(split(element.strip('"')))
        for element in actions:
            rule['actions'].append(split(element.strip('"')))
        return rule
