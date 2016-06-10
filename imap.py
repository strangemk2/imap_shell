import imaplib
import os.path
import time
import ssl

from email.mime.text import MIMEText
from datetime import datetime

import imapidle
import timeout
from aes import imap_shell_aes

imaplib.Debug = 4

Imap_shell_client_pattern = 'ISCP:'
Imap_shell_server_pattern = 'ISSP:'

class imap_session:
    def __init__(self, info):
        self.addr = info['addr']
        self.port = info['port']
        self.user = info['user']
        self.passwd = info['passwd']
        self.mailbox = info['mailbox']
        self.encryption_passwd = info['encryption_passwd']
        self.account = info['account']

    def __enter__(self):
        try:
            self.connection = imaplib.IMAP4_SSL(self.addr, self.port)
        except ssl.SSLError:
            self.connection = imaplib.IMAP4(self.addr, self.port)
        conn = self.connection
        conn.login(self.user, self.passwd)
        conn.select(self.mailbox)

        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        conn = self.connection
        conn.close()
        conn.logout()

    def _active_wait(self, keyword, func, once = False):
        conn = self.connection
        try:
            while True:
                try:
                    with timeout.timeout(seconds = 300):
                        for new_item in conn.idle():
                            conn.done()
                            if once:
                                return self._search_messages(keyword, func)
                            else:
                                self._search_messages(keyword, func)
                except timeout.TimeoutError:
                    #print "timeout."
                    break
                except:
                    raise
        finally:
            conn.done()

    def _lazy_wait(self, keyword, func):
        while True:
            time.sleep(60)
            ret = self._search_messages(keyword, func)
            if ret != 0:
                return ret

    def wait_ISCP(self, func):
        self._active_wait(Imap_shell_client_pattern, func)
        #self._lazy_wait(Imap_shell_client_pattern, func)

    def wait_ISSP(self, func):
        if self._active_wait(Imap_shell_server_pattern, func, once = True) is None:
            self._lazy_wait(Imap_shell_server_pattern, func)

    def _search_messages(self, keyword, func):
        conn = self.connection
        ret = 0
        typ, data = conn.search(None, 'SUBJECT', keyword, 'UNSEEN')
        for num in data[0].split():
            typ, data = conn.fetch(num, "(BODY[TEXT])")
            conn.store(num, '+FLAGS', '\\Seen')
            func(num, data[0][1])
            ret += 1
        return ret

    def search_ISCP(self, func):
        return self._search_messages(Imap_shell_client_pattern, func)

    def search_ISSP(self, func):
        return self._search_messages(Imap_shell_server_pattern, func)

    def _append_impl(self, subject, message):
        conn = self.connection
        message = imap_shell_aes(self.encryption_passwd).encrypt(message)
        conn.append(self.mailbox, None, None,
                    bytearray(make_email(self.account, self.account, subject, message),
                              'utf8'))

    def append_ISCP(self, message):
        """
        Append imap shell client pattern mail to server
        """
        subject = "ISCP: %s" % datetime.now().strftime("%Y%m%d%H%M%S")
        self._append_impl(subject, message)

    def append_ISSP(self, message):
        """
        Append imap shell server pattern mail to server
        """
        subject = "ISSP: %s" % datetime.now().strftime("%Y%m%d%H%M%S")
        self._append_impl(subject, message)


def make_email(from_addr, to_addr, subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr

    return msg.as_string()
