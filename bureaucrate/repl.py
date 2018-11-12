from utils import Config


def repl_main(conf: Config):
    ctx = Config.Context()
    while True:
        resp = input("brcrt > ")
        conf.parse_line(resp, ctx)
