import signal

class imap_shell_signal:
    def __init__(self, func, sig = signal.SIGINT):
        self.sig = sig
        self.func = func

    def __enter__(self):
        self.original_func = signal.getsignal(self.sig)
        signal.signal(self.sig, self.func)

    def __exit__(self, type, value, traceback):
        signal.signal(self.sig, self.original_func)

# http://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python
class GracefulInterruptHandler(object):
    def __init__(self, sig=signal.SIGINT):
        self.sig = sig

    def __enter__(self):
        self.interrupted = False
        self.released = False

        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            self.release()
            self.interrupted = True

        signal.signal(self.sig, handler)

        return self

    def __exit__(self, type, value, tb):
        self.release()

    def release(self):
        if self.released:
            return False

        signal.signal(self.sig, self.original_handler)

        self.released = True

        return True


if __name__ == '__main__':
    import time
    with GracefulInterruptHandler() as h:
        for i in xrange(1000):
            print "..."
            time.sleep(1)
            if h.interrupted:
                print "interrupted!"
                time.sleep(2)
                break
