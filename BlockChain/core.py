###########################################################
# Package: BlockChain
# Filename: core
# Time: Apr 26, 2019 at 3:37:50 PM
############################################################

import json
from flask import Flask     # Used as server and listener
import requests             # Used as client and sender

from node import Node, ConsenseMethod
from block import Block, Certificate
from mycrypto import *

app = Flask(__name__)

with open("config/master.json","r") as f:
    config = json.load(f)
    print(config)

node = Node(config, consensus=ConsenseMethod.PBFT)


if __name__ == '__main__':
    pass