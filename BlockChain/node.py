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
        self.status = False
        self.server = NodeServer(self,self.addr)
        self.core()

    def core(self):
        self.runserver()
        self.find_main()
        while True:
            time.sleep(5)
            if self.mainAddr == self.addr:
                self.set_main(self.peers[random.randint(0, 1)])
            if not self.testalive():
                self.set_main(self.addr)

    def runserver(self):
        self.server.start()

    def find_main(self):
        if not self.mainAddr:
            rets = broadcast(self.peers,dumpjson("getinfo",""))
            for ret in rets:
                if ret != 'Error':
                    self.mainAddr = NodeAddr(ret['main'])
            print("Info: Change Main Address to {}".format(self.mainAddr))

    def set_main(self, addr):
        rets = broadcast(self.peers,dumpjson("setmain_pre",addr))
        count = 0
        success = 0

        for ret in rets:
            if ret != 'Error':
                count += 1
                if ret == True:
                    success += 1

        if isconse(success,count):
            broadcast(self.peers, dumpjson("setmain_after", True))
        else:
            broadcast(self.peers, dumpjson("setmain_after", False))
        self.mainAddr = addr
        print("Info: Change Main Address to {}".format(self.mainAddr))

    def testalive(self, addr = None):
        if not addr:
            addr = self.mainAddr
        ret = sender(self.mainAddr, dumpjson("isalive",""))
        return ret == True


class NodeServer(threading.Thread):
    def __init__(self, node, addr):
        threading.Thread.__init__(self)
        self.ip = addr["ip"]
        self.port = int(addr["port"])
        self.node = node
        self.store = {}                     # 临时存储
        self.route = {}
        self.route['getinfo'] = self.handle_getinfo
        self.route['setmain_pre'] = self.handle_setmain_prev
        self.route['setmain_after'] = self.handle_setmain_after
        self.route['isalive'] = self.handle_isalve

    def run(self):
        s = socket.socket()
        s.bind((self.ip, self.port))
        s.listen(5)
        print("Start Server at {}:{}".format(self.ip, self.port))
        while True:
            client, addr = s.accept()
            recv = str(client.recv(65535), encoding="utf-8")
            ret = self.handle(recv)
            client.send(bytes(dumpjson("", ret), encoding="utf-8"))
            client.close()  # 关闭连接

    def __str__(self):
        return "Server at {}:{}".format(self.ip, self.port)

    def handle(self, msg):
        url,body = loadjson(msg)
        ret = self.route[url](body)
        return ret

    def handle_getinfo(self, msg):
        return {"height": len(self.node.blocks), "main": self.node.mainAddr}

    def handle_setmain_prev(self,msg):
        self.store['mainAddr'] = NodeAddr(msg)
        return True

    def handle_setmain_after(self,msg):
        if msg == True:
            self.node.mainAddr = self.store['mainAddr']
        self.store["mainAddr"] = None
        print("Info: Change Main Address to {}".format(self.node.mainAddr))
        return True

    def handle_isalve(self,msg):
        return True