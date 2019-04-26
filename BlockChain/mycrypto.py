###########################################################
# Package: BlockChain
# Filename: block
# Time: Apr 26, 2019 at 10:44:35 AM
############################################################

from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Hash import SHA256
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
import hashlib
import base64


def gen_keys(priv_file_name, pub_file_name):
    __doc__ = ''' Generate a new pair of keys and save them into files'''

    random_generator = Random.new().read
    rsa = RSA.generate(1024, random_generator)
    priv_key = rsa.exportKey()
    pub_key = rsa.publickey().exportKey()
    with open(priv_file_name,"wb") as f:
        f.write(priv_key)

    with open(pub_file_name,"wb") as f:
        f.write(pub_key)


def open_key(priv_file_name, pub_file_name):
    __doc__ = "Open files, read keys and return"

    pub_key, priv_key = None, None
    with open(priv_file_name,"r") as f:
        key = f.read()
        priv_key = RSA.importKey(key)

    with open(pub_file_name, "r") as f:
        key = f.read()
        pub_key = RSA.importKey(key)
    return priv_key, pub_key


def encrypt(pubkey, text):
    cipher = Cipher_pkcs1_v1_5.new(pubkey)
    C = base64.b64encode(cipher.encrypt(bytes(text, encoding="utf-8")))
    return str(C, encoding="utf-8")


def decrypy(prikey, encrypt_text):
    cipher = Cipher_pkcs1_v1_5.new(prikey)
    text = cipher.decrypt(base64.b64decode(bytes(encrypt_text, encoding="utf-8")), Random.new().read)
    return str(text, encoding= "utf -8")


def sign(prikey, content):
    signer = Signature_pkcs1_v1_5.new(prikey)
    digest = SHA.new()
    digest.update(bytes(content,encoding="utf-8"))
    sign = base64.b64encode(signer.sign(digest))
    return str(sign, encoding="utf-8")


def verify(pubkey,content,sign):
    verifier = Signature_pkcs1_v1_5.new(pubkey)
    digest = SHA.new()
    digest.update(bytes(content,encoding="utf-8"))
    ans = verifier.verify(digest,base64.b64decode(bytes(sign,encoding= "utf-8"))) # True or False
    return ans


def hash(content):
    return SHA256.new(bytes(content, encoding= "utf-8")).hexdigest()

if __name__ == '__main__' :
    gen_keys("priv.pem", "pub.pem")
    priv_key, pub_key = open_key("priv.pem", "pub.pem")

    test1 = "hello,world"
    c = encrypt(pub_key,test1)
    print(c)
    m = decrypy(priv_key,c)
    print(m)

    test2 = "pretent to be a file"
    s = sign(priv_key,test2)
    print(s)
    v = verify(pub_key,test2, s)
    print(v)

    h = hash(test2)
    print(h)
