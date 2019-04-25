###########################################################
# Package: BlockChain
# Filename: block
# Time: Apr 25, 2019 at 9:11:15 PM
############################################################

class Block(object):
    __doc__ = '''This class define the structure of a block'''

    def __init__(self, version, prevblockhash, merkelroothash, timestamp, nonce):
        self.version = version              # Version Number
        self.prevBlockHash = prevblockhash  # PrevBlockHash
        self.merkleRootHash = merkelroothash  # Merkle Root Hash
        self.timeStamp = timestamp          # Time
        self.nonce = nonce                  # Nonce
        self.certificateNumber = 0          # Number of certificates
        self.certificates = []              # List of certificates
        self.sign = []                      # sign used in the PBFT

    def add_certificate(self, cert):
        if isinstance(cert, Certificate):
            raise Exception("Not a Certicate")

        self.certicats.append(cert)
        self.certicateNumber += 1

    def proof_of_work(self):
        raise NotImplemented  # To be Done

    def PBFT(self):
        raise NotImplemented  # To be Done

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
        raise NotImplementedError

