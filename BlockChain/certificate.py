from . import mycrypto

class Certificate(object):

    def __init__(self, version, serial, algorithm, issuer, types,
                 proxyserver, t1, t2, subject, pka, publickey, sign, timestamp, height, loh):
        self.version = version              # Version Number
        self.serial = serial                # Serial Number
        self.types = types                    # Type: Create or Revoke or Update
        self.algorithm = algorithm          # Algorithm ID
        self.issuer = issuer                # Issuer AKA MServer
        self.proxyServer = proxyserver      # Proxy Server
        self.notBefore = t1                 # Validity Not Before
        self.notAfter = t2                  # Validity Not After
        self.subject = subject              # subject

        self.publicKeyAlgorithm = pka       # Public Key Algorithm
        self.subjectPublicKey = publickey   # Public Key Body
        self.Signature = sign               # Certificate Signature
        self.timeStamp = timestamp          # Time Stamp
        self.currentHeight = height         # Current Height
        self.LastOperateHeight = loh        # Last Operation Height

    def create_certificate(self):
        priv_key, pub_key = mycrypto.open_key("priv.pem", "pub.pem")
        hashcert = mycrypto.hash(Certificate)
        sign = mycrypto.sign(priv_key, hashcert)
        self.Signature = sign
