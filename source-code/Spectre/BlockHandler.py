''' 
    A handler for Block.py that takes a collection of blocks (which 
    only reference parents) as input data. It uses a doubly-linked
    tree to determine precedent relationships efficiently, and it can
    use that precedence relationship to produce a reduced/robust  pre-
    cedence relationship as output (the spectre precedence relationship 
    between blocks.
    
    Another handler will extract a coherent/robust list of non-conflict-
    ing transactions from a reduced/robust BlockHandler object.
'''
from Block import *

class BlockHandler(object):
    def __init__(self):
        #print("Initializing")
        # Initialize a BlockHandler object. 
        self.data = None
        self.blocks = {} # Set of blocks (which track parents)
        self.family = {} # Doubly linked list tracks parent-and-child links
        self.invDLL = {} # subset of blocks unlikely to be re-orged
        self.roots = {} # dict {blockIdent : block} root blocks
        self.leaves = {}
        self.antichainCutoff = 600 # stop re-orging after this many layers
        self.pendingVotes = {}
        self.votes = {}
        
    def _addBlocks(self, blocksIn):
        print("Adding Blocks")
        # Take dict of {blockIdent : block} and call _addBlock on each.
        for b in blocksIn:
            self._addBlock(blocksIn[b])
        
    def _addBlock(self, b):
        #print("Adding block")
        # Take a single block b and add to self.blocks, record family
        # relations, update leaf monitor, update root monitor if nec-
        # essary

        diffDict = {copy.deepcopy(b.ident):copy.deepcopy(b)}
        
        try:
            assert b.ident not in self.blocks
        except AssertionError:
            print("Woops, tried to add a block with ident in self.blocks, overwriting old block")
        self.blocks.update(diffDict)

        try:
            assert b.ident not in self.leaves
        except AssertionError:
            print("Woops, tried to add a block to leaf set that is already in the leafset, aborting.")
        self.leaves.update(diffDict) # New block is always a leaf
                
        try:
            assert b.ident not in self.family
        except AssertionError:
            print("woops, tried to add a block that already has a recorded family history, aborting.")
        self.family.update({b.ident:{"parents":b.parents, "children":{}}}) # Add fam history fam

        # Now update each parent's family history to reflect the new child
        if len(b.parents)>0:
            for parentIdent in b.parents:
                if parentIdent not in self.family:
                    # This should never occur.
                    print("Hey, what? confusedTravolta.gif... parentIdent not in self.family, parent not correct somehow.")
                    self.family.update({parentIdent:{}})

                if "parents" not in self.family[parentIdent]:
                    # This should never occur.
                    print("Hey, what? confusedTravolta.gif... family history of parent lacks sub-dict for parentage, parent not correct somehow")
                    self.family[parentIdent].update({"parents":{}})

                if "children" not in self.family[parentIdent]:
                    # This should never occur.
                    print("Hey, what? confusedTravolta.gif... family history of parent lacks sub-dict for children, parent not correct somehow")
                    self.family[parentIdent].update({"children":{}})

                # Make sure grandparents are stored correctly (does nothing if already stored correctly)
                self.family[parentIdent]["parents"].update(self.blocks[parentIdent].parents)
                
                # Update "children" sub-dict of family history of parent
                self.family[parentIdent]["children"].update(diffDict)

                # If the parent was previously a leaf, it is no longer
                if parentIdent in self.leaves:
                    del self.leaves[parentIdent]

        else:
            if b.ident not in self.roots:
                self.roots.update(diffDict)
                self.leaves.update(diffDict)
                self.family.update({b.ident:{"parents":{}, "children":{}}})
        

class Test_RoBlock(unittest.TestCase):
    def test_BlockHandler(self):
        R = BlockHandler()
        b = Block(dataIn="zirconium encrusted tweezers", parentsIn={})
        R._addBlock(b)
        diffDict = {copy.deepcopy(b.ident) : copy.deepcopy(b)}
        #print("Differential ", diffDict)
        b = Block(dataIn="brontosaurus slippers do not exist", parentsIn=copy.deepcopy(diffDict))
        R._addBlock(b)
        #print("Blocks ", R.blocks)
        #print("Family ", R.family)
        #print("Leaves ", R.leaves)
        self.assertEqual(len(R.blocks),2)
        self.assertEqual(len(R.family),2)
        self.assertEqual(len(R.leaves),1)
        #print("Differential ", diffDict)
        key, value = diffDict.popitem()
        #print("Differential ", diffDict)
        #print("Outputted values ", key, value)
        #print("b.ident should = leaf.ident", b.ident)
        self.assertTrue(key in R.blocks)
        self.assertTrue(b.ident in R.blocks)
        self.assertTrue(key in R.family[b.ident]["parents"])
        self.assertTrue(b.ident in R.family[key]["children"])


        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_RoBlock)
unittest.TextTestRunner(verbosity=1).run(suite)
