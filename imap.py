import imaplib
import os.path
import time

from email.mime.text import MIMEText
from datetime import datetime

import imapidle
import timeout
from aes import imap_shell_aes

imaplib.Debug = 5

Imap_shell_client_pattern = 'ISCP:'
Imap_shell_server_pattern = 'ISSP:'

class imap_session:
    def __init__(self, info):
        self.addr = info['addr']
        self.port = info['port']
        self.user = info['user']
        self.passwd = info['passwd']
        self.mailbox = info['mailbox']
        self.account = info['account']

    def _active_wait(self, keyword, func):
        self.connection = imaplib.IMAP4(self.addr, self.port)
        conn = self.connection
        conn.login(self.user, self.passwd)
        conn.select(self.mailbox)
        try:
            while True:
                try:
                    with timeout.timeout(seconds = 300):
                        for new_item in conn.idle():
                            #print "%s new item(s)." % new_item
                            conn.done()
                            self._search_messages(keyword, func)
                except:
                    #print "timeout."
                    break
        finally:
            conn.done()
            conn.close()
            conn.logout()

    def _lazy_wait(self, keyword, func):
        while True:
            time.sleep(60)
            self._search_messages_session(keyword, func)

    def wait_ISCP(self, func):
        self._active_wait(Imap_shell_client_pattern, func)
        self._lazy_wait(Imap_shell_client_pattern, func)

    def wait_ISSP(self, func):
        self._active_wait(Imap_shell_server_pattern, func)
        self._lazy_wait(Imap_shell_server_pattern, func)

    def _search_messages(self, keyword, func):
        conn = self.connection
        typ, data = conn.search(None, 'SUBJECT', keyword, 'NEW')
        for num in data[0].split():
            typ, data = conn.fetch(num, "(BODY[TEXT])")
            func(num, data[0][1])

    def _search_messages_session(self, keyword, func):
        try:
            self.connection = imaplib.IMAP4(self.addr, self.port)
            conn = self.connection
            conn.login(self.user, self.passwd)
            conn.select(self.mailbox)
            self._search_messages(keyword, func)
        finally:
            conn.close()
            conn.logout()

    def recover_ISCP(self, func):
        self._search_messages_session(Imap_shell_client_pattern, func)

    def recover_ISSP(self, func):
        self._search_messages_session(Imap_shell_server_pattern, func)

    def _append_impl(self, subject, message):
        self.connection = imaplib.IMAP4(self.addr, self.port)
        conn = self.connection
        conn.login(self.user, self.passwd)
        message = imap_shell_aes(self.passwd).encrypt(message)
        conn.append(self.mailbox, None, None,
                    bytearray(make_email(self.account, self.account, subject, message),
                              'utf8'))
        conn.logout()

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
