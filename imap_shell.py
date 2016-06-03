import sys

from config import imap_shell_config
from aes import imap_shell_aes
from sig import imap_shell_signal

def client_shell(imap):
    #command_recovery()
    print "> ",
    cmd = sys.stdin.readline()
    while cmd != "":
        cmd = cmd.rstrip()
        if cmd == 'quit':
            break
        elif cmd == '':
            pass
        else:
            imap.send()
            imap.active_wait()
            imap.sleep_wait()

        print "\r> ",
        cmd = sys.stdin.readline()

#def server_batch(imap):
#    if imap.search_imap_shell_messages():
#        process_cmd(messages)
#        imap.active_wait()

config = imap_shell_config('config.ini')

session = imap_shell({
        'addr'    : config('imap_address'),
        'port'    : config('imap_port'),
        'user'    : config('imap_user'),
        'passwd'  : config('imap_passwd'),
        'mailbox' : config('imap_shell_config')})
#enter_shell(imap)
