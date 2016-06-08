# Copyright (c) 2012 Mathieu Lecarme
# This code is licensed under the MIT license (see LICENSE for details)

import imaplib


def idle(connection):
    tag = connection._new_tag()
    cmd = "%s IDLE" % tag
    connection.send("%s\r\n" % cmd)
    if __debug__:
        if connection.debug >= 3:
            connection._mesg("> %s" % cmd);

    response = connection._get_line()
    connection.loop = True
    if response == '+ idling':
        while connection.loop:
            resp = connection._get_line()
            if resp.find("* OK") == -1:
                new, message = resp[2:].split(' ', 1)
                yield new
    else:
        raise Exception("IDLE not handled? : %s" % response)


def done(connection):
    if connection.loop == True:
        if __debug__:
            if connection.debug >= 3:
                connection._mesg("> %s" % 'DONE');

        connection.send("DONE\r\n")
        connection.loop = False

imaplib.IMAP4.idle = idle
imaplib.IMAP4.done = done

if __name__ == '__main__':
    import os
    from lamson.mail import MailRequest
    user = os.environ['EMAIL']
    password = os.environ['PASSWORD']
    print os.environ['SERVER']
    conn = imaplib.IMAP4_SSL(os.environ['SERVER'])
    conn.login(user, password)
    conn.select()
    loop = True
    while loop:
        for uid, msg in conn.idle():
            print uid, msg
            if msg == "EXISTS":
                conn.done()
                status, datas = conn.fetch(uid, '(RFC822)')
                m = MailRequest('localhost', None, None, datas[0][1])
                print m.keys()
                print m.all_parts()
                print m.is_bounce()
