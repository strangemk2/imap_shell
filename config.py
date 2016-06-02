import ConfigParser
import StringIO
import os
from functools import partial

def imap_shell_config(config_file = 'config.ini'):
    fp = StringIO.StringIO()
    fp.write('[section]\n')
    fp.write(open(config_file).read())
    fp.seek(0, os.SEEK_SET)

    config = ConfigParser.ConfigParser()
    config.readfp(fp)

    return partial(config.get, 'section')
