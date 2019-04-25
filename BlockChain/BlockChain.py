############################################################
# Package: BlockChain
# Filename: BlockChain
# Time: Apr 25, 2019 at 8:54:57 PM
############################################################


class BlockChain(object):

    __doc__ = '''This class define the structure of BlockChain'''

    def __init__(self, diffculty):
        self.diffculty = diffculty # Used in the POW
        self.blocks = []

    def add_block(self,block):
        raise NotImplementedError



