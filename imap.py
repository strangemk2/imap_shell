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

    def active_wait(self, func):
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
                            self.search_imap_shell_messages(func)
                except:
                    #print "timeout."
                    break
        finally:
            conn.done()
            conn.close()
            conn.logout()

    def lazy_wait(self, func):
        self.connection = imaplib.IMAP4(self.addr, self.port)
        conn = self.connection
        conn.login(self.user, self.passwd)
        conn.select(self.mailbox)

        try:
            while True:
                time.sleep(60)
                self.search_imap_shell_messages(func)
        finally:
            conn.close()
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

    def _append_impl(self, subject, message):
        self.connection = imaplib.IMAP4(self.addr, self.port)
        conn = self.connection
        conn.login(self.user, self.passwd)
        message = imap_shell_aes(self.passwd).encrypt(response)
        conn.append(self.mailbox, None, None,
                    bytearray(make_email(self.account, self.account, subject, message),
                              'utf8'))
        conn.logout()

    def search_imap_shell_messages(self, func):
        conn = self.connection
        conn.done()
        typ, data = conn.search(None, 'SUBJECT', Imap_shell_client_pattern, 'NEW')
        for num in data[0].split():
            typ, data = conn.fetch(num, "(BODY[TEXT])")
            func(num, data[0][1])

def make_email(from_addr, to_addr, subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr

    return msg.as_string()
