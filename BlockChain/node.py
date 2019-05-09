###########################################################
# Package: BlockChain
# Filename: block
# Time: Apr 26, 2019 at 10:21:36 AM
############################################################

from enum import Enum
import time
import json
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

    def __init__(self, name, config, consensus = ConsenseMethod.POW, diff=5):

        # Ip Config
        self.name = name
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
            nb = Block([])
            nb.init_from_json(json.dumps(block))
            self.blocks.append(nb)

        # Consensus Config
        self.consensus = consensus
        self.status = False
        self.server = NodeServer(self,self.addr)

        # POW
        self.diff = diff
        self.newblock = Block([], height=len(self.blocks), diff=self.diff,
                              timeStamp=None, prevBlockHash="")
        self.alock = threading.Lock()
        self.signal = dict() # 信号 用于事件驱动
        self.signal['needImport'] = True


    def print_block(self):
        for bl in self.blocks:
            print(bl)

    def run(self):
        self.find_main()

        self.runserver()
        while True:
            while self.signal['needImport'] == True:
                self.signal['needImport'] = not self.request_block()
            
            self.import_blocks()
            
            self.newblock.pow()
            self.add_block()


            with open("data/"+ self.name + ".txt","w") as f:
                for bl in self.blocks:
                    f.writelines(bl.__str__() + "\n")

            info = str(random.randint(0, 1000))
            print("send: {}".format(info))
            
            broadcast(self.peers, dumpjson("add", info))
            sender(self.addr, dumpjson("add", info) )

            # if self.addr != self.mainAddr:
            #     self.import_blocks()
            #     info = str(random.randint(0, 1000))
            #     print(info)
            #     ret = sender(self.peers[0], dumpjson("add", info))
            #     time.sleep(5)
            # else:
            #     ret = self.newblock.pow(self.diff)
            #     self.add_block()

    def runserver(self):
        self.server.start()

    def find_main(self):
        if not self.mainAddr:
            rets = broadcast(self.peers,dumpjson("getinfo",""))
            for ret in rets:
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

    # Create a new block used in POW
    def add_block(self):
        self.server.store["cache_lock"].acquire()
        cache = self.server.store['cache'].copy()
        self.server.store['cache'] = []
        self.server.store["cache_lock"].release()

        self.alock.acquire()
        if self.newblock:
            print(self.newblock)
            self.blocks.append(self.newblock)
        self.newblock = Block([], height=len(self.blocks), diff=self.diff, timeStamp=None,
                              prevBlockHash=self.blocks[-1].gethash())
        self.newblock.append(cache)
        self.newblock.flesh(len(self.blocks),self.blocks[-1].gethash())
        self.alock.release()

        # SEND THE NEW BLOCK
        self.boardcast_block(self.blocks[-1])

    def import_blocks(self):
        if len(self.server.tmpBlock) == 0:
            return True
        self.server.tmpBlockLock.acquire()
        cache = self.server.tmpBlock.copy()
        self.server.tmpBlock = []
        self.server.tmpBlockLock.release()

        for js in cache:
            self.import_block(js)
        return True

    # Import a new block from network
    def import_block(self, js):
        self.alock.acquire()
        tmpBlock = Block([])
        ret = tmpBlock.init_from_json(js)
        if ret != -1:
            print("Data Broken.")
            self.signal['needImport'] = True
        elif tmpBlock.height != 0 and tmpBlock.prevBlockHash != self.blocks[-1].gethash():
            print("Error Hash")
            self.signal['needImport'] = True
        elif tmpBlock.height > self.blocks[-1].height + 1:
            print("Error Height")
            self.signal['needImport'] = True
        elif tmpBlock.height <= self.blocks[-1].height:
            print("Warming: Ingore block")
        else:
            self.blocks.append(tmpBlock)
            self.newblock.flesh(len(self.blocks),self.blocks[-1].gethash())
        self.alock.release()

    def boardcast_block(self, bl):
        broadcast(self.peers, dumpjson("resv_block", bl.__str__()))

    # TBD
    def request_block(self):
        rets = broadcast(self.peers,dumpjson('request_block', ''))
        HighestRet = {'height': len(self.blocks), 'data': [bl.__str__() for bl in self.blocks]}
        for ret in rets:
            if ret == 'Error':
                continue
            if ret['height'] > HighestRet['height']:
                HighestRet = ret
        self.server.store["cache_lock"].acquire()
        self.server.store['cache'] = []
        self.server.store["cache_lock"].release()

        self.alock.acquire()
        self.blocks = []
        for js in HighestRet['data']:
            tmpBlock = Block([])
            msg = tmpBlock.init_from_json(js)
            if msg != -1:
                print("Data Broken.")
                return False
            if tmpBlock.height != 0 and tmpBlock.prevBlockHash != self.blocks[-1].gethash():
                print("Error: Hash Error")
                return False
            else:
                self.blocks.append(tmpBlock)
        
        self.newblock.flesh(len(self.blocks), self.blocks[-1].gethash())
        self.alock.release()
        self.print_block()
        return True



        
