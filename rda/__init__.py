from rda.rda import Host, Client, ActionReplayer, ActionRecorder, ScreenReplayer, ScreenRecorder

__all__ = ['Host', 'Client', 'ActionReplayer', 'ActionRecorder', 'ScreenReplayer', 'ScreenRecorder']


import sys


def host():
    return Host()


def client(code=None):
    if code is None:
        code = sys.argv[1:][0]
    return Client(code)
