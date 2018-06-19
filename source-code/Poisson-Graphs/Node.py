from Blockchain import *
from copy import *

class Node(object):
    '''
    Node object. params [identity, blockchain (data), verbosity, difficulty]
    '''
    def __init__(self, params={}):
        self.ident = None
        self.data = {}
        self.verbose = None
        self.edges = {}
        self.mode = None
        self.targetRate = None
        try:
            assert len(params)==5
        except AssertionError:
            print("Error, Tried to create malformed node.")
        else:
            self.ident = params["ident"]
            self.data = params["data"]
            self.verbose = params["verbose"]
            self.edges = {}
            self.mode = params["mode"]
            self.targetRate = params["targetRate"]
            
    def generateBlock(self, discoTime):
        newName = newIdent(len(self.data["blockchain"].blocks))
        t = discoTime
        s = t+self.data["offset"]
        diff = self.data["blockchain"].diff
        params = {"ident":newName, "disco":t, "arriv":s, "parent":None, "diff":diff}
        newBlock = Block(params)
        self.data["blockchain"].addBlock(newBlock)
        return newName
        
    def updateBlockchain(self, incBlocks):
        # incBlocks shall be a dictionary of block identities (as keys) and their associated blocks (as values)
        # to be added to the local data. We assume difficulty scores have been reported honestly for now.
        
        tempData = deepcopy(incBlocks)
        for key in incBlocks:
            if key in self.data["blockchain"].blocks:
                del tempData[key]
            elif incBlocks[key].parent in self.data["blockchain"].blocks or incBlocks[key].parent is None:
                self.data["blockchain"].addBlock(incBlocks[key])
                del tempData[key]
        incBlocks = deepcopy(tempData)
        while len(incBlocks)>0:
            for key in incBlocks:
                if key in self.data["blockchain"].blocks:
                    del tempData[key]
                elif incBlocks[key].parent in self.data["blockchain"].blocks:
                    self.data["blockchain"].addBlock(incBlocks[key], self.mode, self.targetRate)
                    del tempData[key]
            incBlocks = deepcopy(tempData)
            
    def propagate(self, timeOfProp, blockIdent):
        for edgeIdent in self.edges:
            edge = self.edges[edgeIdent]
            length = edge.data["length"]
            timeOfArrival = timeOfProp + length
            otherIdent = edge.getNeighbor(self.ident)
            other = edge.nodes[otherIdent]
            bc = other.data["blockchain"]
            if blockIdent not in bc.blocks:
                pB = edge.data["pendingBlocks"]
                pendingIdent = newIdent(len(pB))
                mybc = self.data["blockchain"]
                blockToProp = mybc.blocks[blockIdent]
                pendingDat = {"timeOfArrival":timeOfArrival, "destIdent":otherIdent, "block":blockToProp}
                pB.update({pendingIdent:pendingDat})
       

class Test_Node(unittest.TestCase):
    # TODO test each method separately
    def test_all(self):
        bill = Blockchain([], verbosity=True)
        mode="Nakamoto"
        tr = 1.0/600000.0
        deltaT = 600000.0
        bill.targetRate = tr
        
        name = newIdent(0)
        t = 0.0
        s = t
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
        genesis = Block(params)
        bill.addBlock(genesis, mode, tr)
        
        parent = genesis.ident
        
        nellyname = newIdent(time.time())
        mode = "Nakamoto"
        targetRate = 1.0/600000.0
        params = {"ident":nellyname, "data":{"offset":0.0, "intensity":1.0, "blockchain":bill}, "verbose":True, "mode":mode, "targetRate":targetRate}
        nelly = Node(params)
        
        while len(nelly.data["blockchain"].blocks) < 2015:
            name = newIdent(len(nelly.data["blockchain"].blocks))
            diff = nelly.data["blockchain"].diff
            t += deltaT*diff*(2.0*random.random()-1.0)
            s = t
            params = {"ident":name, "disco":t, "arriv":s, "parent":parent, "diff":diff}
            newBlock = Block(params)
            nelly.updateBlockchain({newBlock.ident:newBlock})
            parent = name
            
            
        while len(nelly.data["blockchain"].blocks) < 5000:
            name = newIdent(len(nelly.data["blockchain"].blocks))
            diff = nelly.data["blockchain"].diff
            t += deltaT*diff
            s = t
            params = {"ident":name, "disco":t, "arriv":s, "parent":parent, "diff":diff}
            newBlock = Block(params)
            nelly.updateBlockchain({newBlock.ident:newBlock})
            parent = name
        
#suite = unittest.TestLoader().loadTestsFromTestCase(Test_Node)
#unittest.TextTestRunner(verbosity=1).run(suite)
       
