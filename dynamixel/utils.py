import time

class Lock:
    def __init__(self):
        self.locked = False

    def __enter__(self):
        while self.locked:
            time.sleep(.01)
        self.locked = True

    def __exit__(self, *args):
        self.locked = False