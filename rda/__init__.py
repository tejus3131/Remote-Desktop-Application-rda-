from rda.rda import Server, Client, ActionReplayer, ActionRecorder, ScreenReplayer, ScreenRecorder

__all__ = ['Server', 'Client', 'ActionReplayer', 'ActionRecorder', 'ScreenReplayer', 'ScreenRecorder']


import sys


def server():
    return Server()


def client(code=None):
    if code is None:
        code = sys.argv[1:][0]
    return Client(code)
