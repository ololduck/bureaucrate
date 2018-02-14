from sys import argv
from os.path import expanduser, join
from argparse import ArgumentParser

import logging

from . import __version__
from .bureaucrate import init
from .utils import Config


def process_account(conf: Config, account: str):
    acc = init(join(conf.get("base_path"), account))
    for mailbox in conf.get_mailboxes(account):
        for message in acc[mailbox]:
            message.exec_rules(conf.get('rules', [], mailbox, account))


def main():
    parser = ArgumentParser()
    parser.add_argument('--version', help="returns the version and exists")
    parser.add_argument('-a', '--account', help="Restrict to an account")
    parser.add_argument('-c', '--config', default='~/.bureaucraterc',
                        help='specify an alternate configuration file')
    parser.add_argument('--debug', dest='loglevel', help='enable debug logging',
                        action='store_const', const=logging.DEBUG,
                        default=logging.WARNING)
    opts = vars(parser.parse_args(argv[1:]))
    conf = Config()
    conf.parse(expanduser(opts.get('config')))

    from .bureaucrate import logger
    logger.setLevel(opts.get('loglevel'))

    if opts.get('version', None):
        print("bureaucrate v{}".format(__version__))
        return

    if opts.get('account', None):
        process_account(conf, opts.get('account'))
    else:
        for account in conf.get_accounts():
            process_account(conf, account)

if '__main__' in __name__:
    main()
