from BlockChain.node import Node
import json

with open("config/master.json","r") as f:
    config = json.load(f)

node = Node(config)