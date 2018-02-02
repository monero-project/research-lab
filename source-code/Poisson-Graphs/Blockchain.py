from Block import *

class Blockchain(object):
    ''' 
    Not a true blockchain, of course, but tracks block objects (timestamps) as above.
    Each node should be responsible for finding the chain with most cumulative work.
    Right now we assume Nakamoto consensus (konsensnakamoto).
    '''
    def __init__(self, params=[], verbosity=True):
        self.blocks = {}
        self.leaves = {}
        self.miningIdents = None
        self.verbose = verbosity
                
    def addBlock(self, blockToAdd):
        # In our model we assume difficulty scores of blocks are correct (otherwise they would
        # be rejected in the real life network, and we aren't trying to model spam attacks).
        try:
            assert blockToAdd.ident not in self.blocks
        except AssertionError:
            print("Error, tried to add block that already exists in blockchain.")
        else:
            self.blocks.update({blockToAdd.ident:blockToAdd})
            self.leaves.update({blockToAdd.ident:blockToAdd})
            if blockToAdd.parent in self.leaves:
                del self.leaves[blockToAdd.parent]
            self.whichLeaf()
            
    def whichLeaf(self):
        # Determine which leaf shall be the parent leaf.
        # If the chain has forked *ever* this will not be the case.
        maxCumDiff = 0.0
        self.miningIdents = []
        for ident in self.leaves:
            tempCumDiff = 0.0
            thisBlockIdent = ident
            tempCumDiff += self.blocks[thisBlockIdent].diff
            while self.blocks[thisBlockIdent].parent is not None:
                thisBlockIdent = self.blocks[thisBlockIdent].parent
                tempCumDiff += self.blocks[thisBlockIdent].diff
            if tempCumDiff > maxCumDiff:
                # If more than one leaf ties for maxCumDiff, each node in the 
                # network should pick one of these two arbitrarily. Since we 
                # are storing each blockchain in a hash table (unordered!), for 
                # each node in the network that observes a tie, each possible leaf
                # is equally likely to have been the first one found! So
                # we don't need to do anything for the node to select which chain
                # to work off of.
                self.miningIdents = [ident]
                maxCumDiff = tempCumDiff
            elif tempCumDiff == maxCumDiff:
                self.miningIdents.append(ident)
            #print("leaf ident = ", str(ident), ", and tempCumDiff = ", str(tempCumDiff), " and maxCumDiff = ", str(maxCumDiff))
            
           
class Test_Blockchain(unittest.TestCase):
    def test_bc(self):
        bill = Blockchain([], verbosity=True)
        
        name = newIdent(0)
        t = time.time()
        s = t+1
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
        genesis = Block(params)
        
        self.assertEqual(genesis.ident,name)
        self.assertEqual(genesis.discoTimestamp,t)
        self.assertEqual(genesis.arrivTimestamp,t+1)
        self.assertTrue(genesis.parent is None)
        self.assertEqual(genesis.diff,diff)
        
        bill.addBlock(genesis)
        
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertTrue(genesis.ident in bill.leaves)
        self.assertEqual(len(bill.miningIdents),1)
        self.assertEqual(genesis.ident, bill.miningIdents[0])
        
        name = newIdent(1)
        t = time.time()
        s = t+1
        diff = 2.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":genesis.ident, "diff":diff}
        blockA = Block(params)
        bill.addBlock(blockA)
        
        bill.whichLeaf()
        
        self.assertTrue(blockA.ident in bill.blocks)
        self.assertTrue(blockA.ident in bill.leaves)
        self.assertFalse(genesis.ident in bill.leaves)
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertEqual(len(bill.miningIdents),1)
        self.assertEqual(blockA.ident, bill.miningIdents[0])
        
        name = newIdent(1)
        t = time.time()
        s = t+1
        diff = 2.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":genesis.ident, "diff":diff}
        blockB = Block(params)
        bill.addBlock(blockB)
        
        self.assertTrue(blockB.ident in bill.blocks)
        self.assertTrue(blockB.ident in bill.leaves)
        self.assertEqual(bill.blocks[blockB.ident].parent, genesis.ident)
        
        self.assertTrue(blockA.ident in bill.blocks)
        self.assertTrue(blockA.ident in bill.leaves)
        self.assertEqual(bill.blocks[blockA.ident].parent, genesis.ident)
        
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertFalse(genesis.ident in bill.leaves)
        self.assertTrue(bill.blocks[genesis.ident].parent is None)
        
        bill.whichLeaf()
        print(bill.miningIdents)
        
        self.assertEqual(type(bill.miningIdents), type([]))
        self.assertTrue(len(bill.miningIdents), 2)
        
        name = newIdent(2)
        t = time.time()
        diff = 3.14159
        params = {"ident":name, "disco":t, "arriv":s, "parent":blockB.ident, "diff":diff}
        blockC = Block(params)
        bill.addBlock(blockC)
        
        self.assertTrue(blockC.ident in bill.blocks)
        self.assertTrue(blockC.ident in bill.leaves)
        
        self.assertTrue(blockB.ident in bill.blocks)
        self.assertFalse(blockB.ident in bill.leaves)
        
        self.assertTrue(blockA.ident in bill.blocks)
        self.assertTrue(blockA.ident in bill.leaves)
        
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertFalse(genesis.ident in bill.leaves)
        
        bill.whichLeaf()
        
        #for blockIdent in bill.blocks:
        #    ident = bill.blocks[blockIdent].ident
        #    disco = bill.blocks[blockIdent].discoTimestamp
        #    arriv = bill.blocks[blockIdent].arrivTimestamp
        #    parent = bill.blocks[blockIdent].parent
        #    diff = bill.blocks[blockIdent].diff
        #    print(str(ident) + ", " + str(disco) + ", " + str(arriv) + ", " + str(parent) + ", " + str(diff) + ", " + str() + "\n")
        #print(bill.miningIdents)
        self.assertEqual(len(bill.miningIdents), 1)
        self.assertEqual(bill.miningIdents[0], blockC.ident)
        
       
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_Blockchain)
unittest.TextTestRunner(verbosity=1).run(suite)
