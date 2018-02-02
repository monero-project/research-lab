from Node import *
                
class Edge(object):
    '''
    Edge object. Has an identity, some data, and a dict of nodes.
    '''
    def __init__(self, params=["", {}, True]):
        try:
            assert len(params)==3
        except AssertionError:
            print("Error, tried to create mal-formed edge.")
        else:
            self.ident = params[0]
            self.data = params[1]
            self.verbose = params[2]
            self.nodes = {}
        
    def getNeighbor(self, nodeIdent):
        # Given one node identity, check that the node
        # identity is in the edge's node list and 
        # return the identity of the other adjacent node.
        result = (nodeIdent in self.nodes)
        if result:
            for otherIdent in self.nodes:
                if otherIdent != nodeIdent:
                    result = otherIdent
        assert result in self.nodes
        return result
        
class Test_Edge(unittest.TestCase):
    def test_e(self):
        nellyIdent = newIdent(0)
        bill = Blockchain([], verbosity=True)
        
        name = newIdent(0)
        t = time.time()
        diff = 1.0
        params = [name, t, t+1, None, diff, bill.verbose] # Genesis block has no parent, so parent = None
        genesis = Block(params)
        bill.addBlock(genesis)
        
        time.sleep(10)
        
        name = newIdent(1)
        t = time.time()
        diff = 1.0
        params = [name, t, t+1, genesis.ident, diff, bill.verbose]
        blockA = Block(params)
        bill.addBlock(blockA)
        
        # Nodes need an identity and a blockchain object and verbosity and difficulty
        nelly = Node([nellyIdent, copy.deepcopy(bill), bill.verbosity, diff])
        nelly.updateDifficulty(mode="Nakamoto")
        
        time.sleep(9)
        
        name = newIdent(len(nelly.data))
        t = time.time()
        params = [name, t, t+1, blockA.ident, nelly.diff, nelly.verbose]
        blockB = Block(params)
        nelly.updateBlockchain({blockB.ident:blockB})
        
        time.sleep(8)
        
        name = newIdent(len(nelly.data))
        t = time.time()
        params = [name, t, t+1, blockB.ident, nelly.diff, nelly.verbose]
        blockC = Block(params)
        nelly.updateBlockchain({blockC.ident:blockC})
        
        time.sleep(1)
        name = newIdent(len(nelly.data))
        t = time.time()
        params = [name, t, t+1, blockB.ident, nelly.diff, nelly.verbose] # Fork off
        blockD = Block(params)
        nelly.updateBlockchain({blockD.ident:blockD})
        
        time.sleep(7)
        name = newIdent(len(nelly.data))
        t = time.time()
        params = [name, t, t+1, blockD.ident, nelly.diff, nelly.verbose] 
        blockE = Block(params)
        nelly.updateBlockchain({blockE.ident:blockE})
        
        
        time.sleep(6)
        name = newIdent(len(nelly.data))
        t = time.time()
        params = [name, t, t+1, blockE.ident, nelly.diff, nelly.verbose] 
        blockF = Block(params)
        nelly.updateBlockchain({blockF.ident:blockF})
        
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_Edge)
unittest.TextTestRunner(verbosity=1).run(suite)
