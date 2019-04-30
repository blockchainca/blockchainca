from BlockChain.node import Node
import json

with open("config/slave1.json","r") as f:
    config = json.load(f)

node = Node(config)