import threading
import json
import socket
from .client import *
from .mycrypto import *
from .node import Node, NodeAddr

class NodeServer(threading.Thread):
    def __init__(self, node, addr):
        threading.Thread.__init__(self)
        self.ip = addr["ip"]
        self.port = int(addr["port"])
        self.node = node
        self.store = dict()                     # 临时存储
        self.store['cache'] = []
        self.store['cache_lock'] = threading.Lock()
        self.route = dict()
        self.route['getinfo'] = self.handle_getinfo
        self.route['setmain_pre'] = self.handle_setmain_prev
        self.route['setmain_after'] = self.handle_setmain_after
        self.route['isalive'] = self.handle_isalve
        self.route['add'] = self.handle_add
        self.route['add'] = self.handle_add
        self.route['resv_block'] = self.handle_resv_block

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
        if msg:
            self.node.mainAddr = self.store['mainAddr']
        self.store["mainAddr"] = None
        print("Info: Change Main Address to {}".format(self.node.mainAddr))
        return True

    def handle_isalve(self, msg):
        return True

    def handle_add(self, data):
        print("resv: {}".format(data))
        self.store['cache_lock'].acquire()
        self.store['cache'].append(data)
        self.store['cache_lock'].release()
        return True

    def handle_resv_block(self,js):
        # print("resv block: {}".format(js))
        self.node.import_block(js)
        self.node.print_block()
        return True