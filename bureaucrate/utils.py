import datetime


def parse_timespec(timespec: str) -> datetime.timedelta:
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
    return datetime.timedelta(days=days, seconds=seconds)
