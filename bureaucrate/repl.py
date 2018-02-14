from utils import Config


def parse_line(resp: str, conf: Config):
    pass


def replmain(conf: Config):
    while True:
        resp = input("brcrt > ")
        parse_line(resp, conf)
