import imaplib
import os.path
import time

import imapidle
import timeout

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

    def active_wait(self):
        self.connection = imaplib.IMAP4(self.addr, self.port)
        conn = self.connection
        conn.login(self.user, self.passwd)
        conn.select(self.mailbox)
        try:
            while True:
                try:
                    with timeout.timeout(seconds = 300):
                        for new_item in conn.idle():
                            print "%s new item(s)." % new_item
                            self.search_imap_shell_messages()
                except:
                    print "timeout."
                    break
        finally:
            conn.done()
            conn.close()
            conn.logout()

    def lazy_wait(self):
        self.connection = imaplib.IMAP4(self.addr, self.port)
        conn = self.connection
        conn.login(self.user, self.passwd)
        conn.select(self.mailbox)

        try:
            while True:
                time.sleep(60)
                self.wait_once()
        finally:
            conn.close()
            conn.logout()

    def send_ISCP(cmd):
        pass

    def send_ISSP(cmd):
        pass

    def search_imap_shell_messages(self):
        conn = self.connection
        conn.done()
        typ, data = conn.search(None, 'SUBJECT', Imap_shell_client_pattern, 'NEW')
        for num in data[0].split():
            typ, data = conn.fetch(num, "(BODY[TEXT])")
            print('Message %s\n%s\n' % (num, data[0][1]))
