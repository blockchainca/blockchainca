import socket
import time
import random
from BlockChain.client import *
from BlockChain.node import NodeAddr

dic = [
    {'ip': "127.0.0.1", 'port': 6000},
    {'ip': "127.0.0.1", 'port': 6002},
    {'ip': "127.0.0.1", 'port': 6004},
]

peers = []

count = 0

def init_peers():
    for peer in dic:
        peers.append(NodeAddr(peer))

def send_data():
    global count
    print("send: {}".format(str(count)))
    broadcast(peers, dumpjson("add", str(count)))
    count += 1

if __name__ == "__main__":
    init_peers()
    while True:
        send_data()
        time.sleep(5)