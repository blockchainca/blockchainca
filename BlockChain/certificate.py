import time
import random
import json
from datetime import datetime,timedelta
from dataclasses import dataclass, field
from . import mycrypto

@dataclass
class UUIDGenerator(object):
    name: str = "node"
    count: int = 0
    salt: str = "salt123"

    def change_addr(self,name, salt = "salt123"):
        self.name = name
        self.salt = salt
    
    def get_uuid(self):
        self.count += 1
        return self.name + \
        str(int(time.time() * 100000)) + \
        mycrypto.hash( str(self.count) + self.salt)

uug = UUIDGenerator()

def factory_not_before():
    return datetime.now().timestamp()

def factory_not_after():
    now = datetime.now()
    notafter = now + timedelta(days = 365) 
    return notafter.timestamp()

@dataclass
class Certificate(object):

    version: int = 1    # Version Number
    serial: str = field(default_factory=uug.get_uuid)    # Serial Number
    types:  str = "Create" # Type: Create or Revoke or Update
    algorithm: str = "rsa1024" # Algorithm
    proxyServer: str = ""
    notBefore: any = field(default_factory=factory_not_before)
    notAfter: any = field(default_factory=factory_not_after)
    subject: str = "1231231231" # phone or email
    pub_key: str = field(default="123")
    publicKeyAlgorithm: str = "rsa1024"
    Signature: str = field(default= '',repr = False)
    timeStamp: any = field(default_factory=factory_not_before)
    currentHeight: int = field(default= -1,repr = False)
    LastOperateHeight: int = field(default= -1,repr = False)

    def get_js(self):
        # 获取所以属性的 json 字符串，用于传输
        return json.dumps(self.__dict__)
    
    def sign_content(self):
        return str(self)

    def create_certificate(self, priv_key):
        hashcert = mycrypto.hash(self.sign_content())
        sign = mycrypto.sign(priv_key, hashcert)
        self.Signature = sign

    def __eq__(self, other):
        return self.subject == other.subject and self.serial == other.serial