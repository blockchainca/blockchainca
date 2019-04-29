###########################################################
# Package: BlockChain
# Filename: block
# Time: Apr 26, 2019 at 10:21:36 AM
############################################################

from enum import Enum
import json
from .block import Block


class NodeAddr(dict):
    __doc__ = "network addr"

    def __init__(self, addr_dict):
        super(NodeAddr,self).__init__()
        self["ip"] = addr_dict["ip"]
        self["port"] = addr_dict["port"]
        try:
            self["sport"] = addr_dict["sport"]
        except KeyError:
            self["sport"] = None



class ConsenseMethod(Enum):
    # 共识机制的编号 ... 可能只实现其中一个
    POW = 0
    PBFT = 1


class Node(object):

    __doc__ = "This is a node in the block chain network"

    def __init__(self, config, consensus = ConsenseMethod.PBFT):

        # Ip Config
        self.addr = NodeAddr(config["addr"])    # Address
        self.peers = []                         # Other nodes in the network
        for peer in config['peers']:
            self.peers.append(NodeAddr(peer))
        self.isMain = config["role"] == 1    # Is Main Server

        if self.isMain :
            self.mainAddr = self.addr
        else:
            self.mainAddr = None

        # Data Config
        self.blocks = []
        for block in config["block"]:
            self.blocks.append(Block(block))

        # Consensus Config
        self.consensus = consensus
