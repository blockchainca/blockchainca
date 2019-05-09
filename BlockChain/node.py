###########################################################
# Package: BlockChain
# Filename: block
# Time: Apr 26, 2019 at 10:21:36 AM
############################################################

from enum import Enum
import time
import threading,socket
import random
from .block import Block
from .server import NodeServer
from .client import sender, broadcast, loadjson, dumpjson, isconse


class NodeAddr(dict):
    __doc__ = "network addr"

    def __init__(self, addr_dict):
        super(NodeAddr,self).__init__()
        self["ip"] = addr_dict["ip"]
        self["port"] = addr_dict["port"]

    def __eq__(self, other):
        return self["ip"] == other["ip"] and self["port"] == other["port"]


class ConsenseMethod(Enum):
    # 共识机制的编号 ... 可能只实现其中一个
    POW = 0
    PBFT = 1


class Node(object):

    __doc__ = "This is a node in the block chain network"

    def __init__(self, config, consensus = ConsenseMethod.PBFT, diff=4):

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
        for idx, block in enumerate(["block"]):
            self.blocks.append(Block(block, diff=diff, height=idx))

        # Consensus Config
        self.consensus = consensus
        self.status = False
        self.server = NodeServer(self,self.addr)

        # POW
        self.diff = diff
        self.newblock = Block([], height=len(self.blocks), diff=self.diff,
                              timeStamp=None, prevBlockHash="")
        self.alock = threading.Lock()

        # Start
        self.core()

    def print_block(self):
        for bl in self.blocks:
            print(bl)

    def core(self):
        self.runserver()
        self.find_main()

        while True:
            if self.addr != self.mainAddr:
                info = str(random.randint(0, 1000))
                print(info)
                ret = sender(self.peers[0], dumpjson("add", info))
                time.sleep(3)
            else:
                ret = self.newblock.pow(self.diff)
                self.add_block()

    def runserver(self):
        self.server.start()

    def find_main(self):
        if not self.mainAddr:
            rets = broadcast(self.peers,dumpjson("getinfo",""))
            for ret in rets:
                print(ret)
                if ret != 'Error':
                    self.mainAddr = NodeAddr(ret['main'])
                    break
            print("Info: Change Main Address to {}".format(self.mainAddr))

    def set_main(self, addr):
        rets = broadcast(self.peers,dumpjson("setmain_pre",addr))
        count = 0
        success = 0

        for ret in rets:
            if ret != 'Error':
                count += 1
                if ret:
                    success += 1

        if isconse(success,count):
            broadcast(self.peers, dumpjson("setmain_after", True))
        else:
            broadcast(self.peers, dumpjson("setmain_after", False))
        self.mainAddr = addr
        print("Info: Change Main Address to {}".format(self.mainAddr))

    def testalive(self, addr=None):
        if not addr:
            addr = self.mainAddr
        ret = sender(self.mainAddr, dumpjson("isalive",""))
        return ret == True

    # Create a new block
    def add_block(self):
        self.server.store["cache_lock"].acquire()
        cache = self.server.store['cache']
        self.server.store['cache'] = []
        self.server.store["cache_lock"].release()

        self.alock.acquire()
        if self.newblock:
            print(self.newblock)
            self.blocks.append(self.newblock)
        self.newblock = Block([], height=len(self.blocks), diff=self.diff, timeStamp=None,
                              prevBlockHash=self.blocks[-1].gethash())
        self.newblock.append(cache)
        self.newblock.flesh(len(self.blocks))
        self.alock.release()

        # SEND THE NEW BLOCK
        self.boardcast_block(self.blocks[-1])

    # Import a new block from network
    def import_block(self, js):
        self.alock.acquire()
        tmpBlock = Block([])
        ret = tmpBlock.init_from_json(js)
        if ret != -1:
            print("Data Broken.")
        # elif tmpBlock.prevBlockHash != self.blocks[-1].gethash():
        #     print("Error Hash")
        # elif tmpBlock.height != self.blocks[-1].height + 1:
        #     print("Error Height")
        else:
            self.blocks.append(tmpBlock)
            # TBD
            self.newblock.flesh(len(self.blocks))
        self.alock.release()

    def boardcast_block(self, bl):
        broadcast(self.peers, dumpjson("resv_block", bl.__str__()))

    # TBD
    def request_block(self, height):
        return True


        
