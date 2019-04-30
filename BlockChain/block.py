###########################################################
# Package: BlockChain
# Filename: block
# Time: Apr 25, 2019 at 9:11:15 PM
############################################################

import time
import json
from . import mycrypto
import threading



class Block(object):
        __doc__ = '''This class define the structure of a block'''

        version = 1                             # Version Number
        prevBlockHash = ""                      # PrevBlockHash
        merkleTree = None                       # Merkle Tree
        timeStamp = 0                           # Time
        nonce = 0                               # Nonce
        data = []                               # Data
        sign = []                               # sign used in the PBFT

        def __init__(self, data, diff = 5, timeStamp = None, prevBlockHash = ""):
            self.version = 1
            self.nonce = 0
            self.sign = []
            self.diff = diff
            self.data = data
            self.prevBlockHash = prevBlockHash
            if not timeStamp:
                self.timeStamp = time.time()
            else:
                self.timeStamp = timeStamp
            self.merkleTree = MerkleTree(self.data)
            self.pow(diff=self.diff)

        def __str__(self):
            return json.dumps(self.__dict__)

        def gethash(self):
            return mycrypto.hash(self.__str__())

        def append(self,new_data):
            self.data.extend(new_data)

        def flesh(self):
            self.timeStamp = time.time()
            self.merkleTree = MerkleTree(self.data)
            self.nonce = 0

        def pow(self, diff=5):
            while True:
                if self.verify(diff):
                    break
                self.nonce += 1
            return True

        def verify(self, diff):
            return int(self.gethash()[0:diff], 16) == 0


# Merkle Tree
class MerkleTree(list):

    def __init__(self, data):
        total, leaf_start = get2pow(len(data))
        super(MerkleTree,self).__init__(['']*total)

        ii = leaf_start
        for each in data:
            self[ii] = self.optc(each)
            ii += 1

        p = leaf_start - 1
        end = len(self) - 1

        while p >= 0:
            self[p] = self.optc(self[end] + self[end - 1])
            p -= 1
            end -= 2

    def optc(self,elem):
        return mycrypto.hash(str(elem))
        #return elem


def get2pow(l):
    h = 1
    while h < l:
        h *= 2

    # tmp = []
    # tmp.append(l)
    # while tmp[-1] != 1:
    #     tmp.append(int(tmp[-1]/2 + 0.5))
    #     total = sum(tmp)
    return 2*h - 1, h - 1


if __name__ == '__main__':
    print(MerkleTree([1,2,3,4,5]))
