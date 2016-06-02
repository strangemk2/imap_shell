# timeout
import signal
import time

import sys

if sys.version_info.major == 2:
    class TimeoutError(Exception):
        pass

class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)

if __name__ == '__main__':
    with timeout(seconds=3):
        time.sleep(4)
