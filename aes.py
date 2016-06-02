import os.path
import sys
import os
import hashlib
import base64
import pickle
import zlib
import StringIO

sys.path.append(os.path.dirname(__file__) + "/./lib")
import pyaes

class imap_shell_aes:
    def __init__(self, password):
        self.key = hashlib.sha256(password).digest()

    def encrypt(self, data):
        iv = os.urandom(16)

        aes = pyaes.AESModeOfOperationCBC(self.key, iv = iv)
        data = zlib.compress(data)
        length = len(data)
        ciphertext = ''
        for r in alignment_read(data, 16):
            ciphertext = ciphertext + aes.encrypt(r)

        return base64.b64encode(zlib.compress(pickle.dumps(
                {'len'        : length,
                 'iv'         : iv,
                 'ciphertext' : ciphertext,
                 'hash'       : hashlib.md5(data).hexdigest()})))

    def decrypt(self, data):
        encrypted_data = pickle.loads(zlib.decompress(base64.b64decode(data)))
        aes = pyaes.AESModeOfOperationCBC(self.key, iv = encrypted_data['iv'])
        decrypted = ''
        for r in alignment_read(encrypted_data['ciphertext'], 16):
            decrypted = decrypted + aes.decrypt(r)

        if (len(decrypted) > encrypted_data['len']):
            decrypted = decrypted[:encrypted_data['len']]

        if hashlib.md5(decrypted).hexdigest() != encrypted_data['hash']:
            raise Exception('Unexpected aes data.')
        else:
            return zlib.decompress(decrypted)

def alignment_read(data, size):
    fp = StringIO.StringIO(data)
    while True:
        ret = fp.read(size)
        if (len(ret) == 0):
            break
        elif (len(ret) < size):
            yield ret.ljust(size)
        else:
            yield ret

if __name__ == '__main__':
    aes = imap_shell_aes('Atadm')
    plaintext = "alsdkjflkbhiojwhler9023ujiok;kmlzv;xckja;lsdfkj"
    res = aes.encrypt(plaintext)
    ori = aes.decrypt(res)
    print plaintext
    print res
    print ori

    text = '1'
    for r in alignment_read(text, 3):
        print '"%s"' % r
