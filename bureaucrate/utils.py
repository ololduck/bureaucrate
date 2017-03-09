import datetime


def parse_timespec(timespec: str) -> datetime.timedelta:
    """
    returns a negative timedelta corresponding to the given timespec
    :param timespec: a space-delimited string of time info. see examples
    :return:
    """
    elements = timespec.split()
    delta = datetime.timedelta()
    for e in elements:
        if e[-1:] == 'd':
            delta.days = int(e[:-1])
        if e[-1:] == 'M':
            delta.days -= int(e[:-1]) * 30
        if e[-1:] == 'y':
            delta.days -= int(e[:-1]) * 365
        if e[-1:] == 'h':
            delta.seconds -= int(e[:-1]) * 3600
        if e[-1:] == 'm':
            delta.seconds -= int(e[:-1]) * 60
        if e[-1:] == 's':
            delta.seconds -= int(e[:-1])
    return delta
