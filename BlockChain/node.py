###########################################################
# Package: BlockChain
# Filename: block
# Time: Apr 26, 2019 at 10:21:36 AM
############################################################

from Crypto.PublicKey import RSA
import requests
from enum import Enum


class ConsenseMethod(Enum):
    # 共识机制的编号 ... 可能只实现其中一个
    POW = 0
    PBFT = 1


class Node(object):

    __doc__ = "This is a node in the block chain network"

    def __init__(self, config, consensus = ConsenseMethod.PBFT):
        self.ip = config['ip']        # Ip Address
        self.peers = config['peers']      # Other nodes in the network
        self.isMain = config['role'] == "master"    # Is Main Server?
        self.mainAddress = None # Main Server's Ip Address
        self.blocks = []
        self.consensus = consensus

    def add_block(self,block):
        raise NotImplemented