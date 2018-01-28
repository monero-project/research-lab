import unittest, copy, random, math, time
from scipy.stats import skew
from numpy import var
from numpy import random as nprandom

#TODO: Node.data["blockchain"] != node.data

def newIdent(params):
    nonce = params
    # Generate new random identity.
    return hash(str(nonce) + str(random.random()))
    
def newIntensity(params):
    mode = params
    if mode=="uniform":
        return random.random()
        
def newOffset(params):
    mode = params
    if mode=="unifDST":
        r = 2.0*random.random() - 1.0 # hours
        r = 60.0*60.0*r #60 min/hr, 60 sec/min
        return r
    if mode=="sumOfSkellams":
        # This mode uses a skellam distribution, which is
        # the difference of two poisson-distributed random 
        # variables.
        # HourOffset = skellam
        # SecondOffset = skellam
        # TotalOffset = 60*60*HourOffset + 60*MinuteOffset + SecondOffset
        # Each skellam = poisson(1) - poisson(1)
        # Reasoning: We consider most computers' local time offset from UTC
        # to be a two time-scale random variable, one on the hour scale and one on 
        # the second scale. We make 
        x = nprandom.poisson(1, (2,2))
        totalOffset = 60.0*60.0*float(x[0][0] - x[1][0]) + float((x[0][1] - x[1][1]))
        return totalOffset

class StochasticProcess(object):
    ''' 
    Stochastic processes have a clock and a state.
    The clock moves forward, and then the state updates.
    More detail requires knowledge of the underlying stochProc.
    '''
    def __init__(self, params=None):
        # initialize with initial data
        self.data = params
        self.t = 0.0 # should always start at t=0.0
        self.state = 0.0 # magic number
        self.maxTime = 1000.0 # magic number
        self.verbose = True
        
    def go(self):
        # Executes stochastic process.
        assert self.maxTime > 0.0 # Check loop will eventually terminate.
        t = self.t
        while t <= self.maxTime: 
            deltaT = self.getNextTime() # Pick the next "time until event" and a description of the event.
            self.updateState(t, deltaT) # Update state with deltaT input
            t = self.t
            if self.verbose:
                print("Recording...")
            
    def getNextTime(self):
        return 1 # Magic number right now
        
    def updateState(self, t, deltaT):
        # Update the state of the system. In this case,
        # we are doing a random walk on the integers.
        self.state += random.randrange(-1,2,1) # [-1, 0, 1]
        self.t += deltaT
    
class Test_StochasticProcess(unittest.TestCase):
    def test_sp(self):
        sally = StochasticProcess()
        sally.go()
        
#suite = unittest.TestLoader().loadTestsFromTestCase(Test_StochasticProcess)
#unittest.TextTestRunner(verbosity=1).run(suite)

class Block(object):
    '''
    Each block has: an identity, a timestamp of discovery (possibly false), 
    has a timestamp of arrival at the local node (possibly unnecessary), a pointer to a parent
    block's identity, and a difficulty score.
    '''
    def __init__(self, params=[]):
        try:
            assert len(params)==6
        except AssertionError:
            print("Error in Block(): Tried to add a malformed block. We received params = " + str(params) + ", but should have had something of the form [ident, disco, arriv, parent, diff, verbose].")
        else:
            self.ident = params[0]
            self.discoTimestamp = params[1]
            self.arrivTimestamp = params[2]
            self.parent = params[3]
            self.diff = params[4]
            self.verbose = params[5]
        
class Test_Block(unittest.TestCase):
    def test_b(self):
        #bill = Block()
        name = newIdent(0)
        t = time.time()
        diff = 1.0
        params = [name, t, t+1, None, diff, False]
        bill = Block(params)
        self.assertEqual(bill.ident,name)
        self.assertEqual(bill.discoTimestamp,t)
        self.assertEqual(bill.arrivTimestamp,t+1)
        self.assertTrue(bill.parent is None)
        self.assertEqual(bill.diff,diff)
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_Block)
unittest.TextTestRunner(verbosity=1).run(suite)
            
class Blockchain(object):
    ''' 
    Not a true blockchain, of course, but tracks block objects (timestamps) as above.
    Each node should be responsible for finding the chain with most cumulative work.
    Right now we assume Nakamoto consensus (konsensnakamoto).
    '''
    def __init__(self, params=[], verbosity=True):
        self.blocks = {}
        self.leaves = {}
        self.miningIdent = None
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
        if len(self.leaves) == 1:
            # If the chain has never forked, we have no decision to make:
            for ident in self.leaves:
                self.miningIdent = ident
        elif len(self.leaves) > 1:
            # If the chain has forked *ever* this will not be the case.
            maxCumDiff = 0.0
            for ident in self.leaves:
                tempCumDiff = 0.0
                tempCumDiff += self.blocks[ident].diff
                nextIdent = self.blocks[ident].parent
                if nextIdent is not None and nextIdent in self.blocks:
                    while self.blocks[nextIdent].parent is not None:
                        tempCumDiff += self.blocks[nextIdent].diff
                        nextIdent = self.blocks[nextIdent].parent
                if tempCumDiff > maxCumDiff:
                    # If more than one leaf ties for maxCumDiff, each node in the 
                    # network should pick one of these two arbitrarily. Since we 
                    # are storing each blockchain in a hash table (unordered!), for 
                    # each node in the network that observes a tie, each possible leaf
                    # is equally likely to have been the first one found! So
                    # we don't need to do anything for the node to select which chain
                    # to work off of.
                    self.miningIdent = ident
        else:
            print("Error, tried to assess an empty blockchain.")
           
class Test_Blockchain(unittest.TestCase):
    def test_bc(self):
        bill = Blockchain([], verbosity=True)
        
        name = newIdent(0)
        t = time.time()
        diff = 1.0
        params = [name, t, t+1, None, diff, bill.verbose]
        genesis = Block(params)
        
        self.assertEqual(genesis.ident,name)
        self.assertEqual(genesis.discoTimestamp,t)
        self.assertEqual(genesis.arrivTimestamp,t+1)
        self.assertTrue(genesis.parent is None)
        self.assertEqual(genesis.diff,diff)
        
        bill.addBlock(genesis)
        
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertTrue(genesis.ident in bill.leaves)
        self.assertEqual(genesis.ident, bill.miningIdent)
        
        name = newIdent(1)
        t = time.time()
        diff = 2.0
        params = [name, t, t+1, genesis.ident, diff, bill.verbose]
        blockA = Block(params)
        bill.addBlock(blockA)
        
        self.assertTrue(blockA.ident in bill.blocks)
        self.assertTrue(blockA.ident in bill.leaves)
        self.assertFalse(genesis.ident in bill.leaves)
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertEqual(blockA.ident, bill.miningIdent)
        
        name = newIdent(1)
        t = time.time()
        diff = 2.5
        params = [name, t, t+1, None, diff, bill.verbose]
        blockB = Block(params)
        bill.addBlock(blockB)
       
        self.assertTrue(blockB.ident in bill.blocks)
        self.assertTrue(blockB.ident in bill.leaves)
        self.assertFalse(genesis.ident in bill.leaves)
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertTrue(blockA.ident in bill.leaves)
        self.assertTrue(blockB.ident in bill.leaves)
        self.assertEqual(blockB.ident, bill.miningIdent)
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_Blockchain)
unittest.TextTestRunner(verbosity=1).run(suite)
        
class Node(object):
    '''
    Node object. params [identity, blockchain (data), verbosity, difficulty]
    '''
    def __init__(self, params=["", {}, True]):
        try:
            assert len(params)==4
        except AssertionError:
            print("Error, Tried to create malformed node.")
        else:
            self.ident = params[0]
            self.data = params[1] #Blockchain object
            self.verbose = params[2]
            self.diff = params[3]
            self.edges = {}
        
    def updateBlockchain(self, incBlocks, diffUpdateRate=1, mode="Nakamoto", targetRate=1.0/1209600.0):
        # dataToUpdate shall be a dictionary of block identities (as keys) and their associated blocks (as values)
        # to be added to the local data. We assume difficulty scores have been reported honestly for now.
        
        # Stash a copy of incoming blocks so removing keys won't shrink the size of the dictionary over which
        # we are looping.
        tempData = copy.deepcopy(incBlocks)
        for key in incBlocks:
            if incBlocks[key].parent in self.data["blockchain"].blocks:
                self.data["blockchain"].addBlock(incBlocks[key])
                #if len(self.data["blockchain"]) % diffUpdateRate == 0:
                #    self.updateDifficulty(mode, targetRate)
                del tempData[key]
        incBlocks = copy.deepcopy(tempData)
        while len(incBlocks)>0:
            for key in incBlocks:
                if incBlocks[key].parent in self.data["blockchain"].blocks:
                    self.data["blockchain"].addBlock(incBlocks[key])
                    #if len(self.data["blockchain"]) % diffUpdateRate == 0:
                    #    self.updateDifficulty(mode, targetRate)
                    del tempData[key]
            incBlocks = copy.deepcopy(tempData)
            
    def updateDifficulty(self, mode="Nakamoto", targetRate=1.0/1209600.0):
        # Compute the difficulty of the next block
        # Note for default, targetRate = two weeks/period, seven days/week, 24 hours/day, 60 minutes/hour, 60 seconds/minute) = 1209600 seconds/period
        if mode=="Nakamoto":
            # Use MLE estimate of poisson process, compare to targetRate, update by multiplying by resulting ratio.
            count = 2016
            ident = self.data.miningIdent
            topTime = copy.deepcopy(int(round(self.data.blocks[ident].discoTimestamp)))
            parent = self.data.blocks[ident].parent
            count = count - 1
            while count > 0 and parent is not None:
                ident = copy.deepcopy(parent)
                parent = self.data.blocks[ident].parent
                count = count - 1
            botTime = copy.deepcopy(int(round(self.data.blocks[ident].discoTimestamp)))
            
            # Algebra is okay:
            assert 0 <= 2016 - count and 2016 - count < 2017
            assert topTime > botTime
            
            # MLE estimate of arrivals per second:
            mleDiscoRate = float(2016 - count)/float(topTime - botTime)
            
            # How much should difficulty change?
            self.diff = self.diff*(mleDiscoRate/targetRate)
            
        elif mode=="vanSaberhagen":
            # Similar to above, except use 1200 blocks, discard top 120 and bottom 120 after sorting.
            # 4 minute blocks in the original cryptonote, I believe... targetRate = 1.0/
            # 4 minutes/period, 60 seconds/minute ~ 240 seconds/period
            assert targetRate==1.0/240.0
            count = 1200
            ident = self.data.miningIdent
            bl = []
            bl.append(copy.deepcopy(self.data.blocks[ident].discoTimestamp))
            parent = self.data.blocks[ident].parent
            count = count - 1
            while count > 0 and parent is not NOne:
                ident = copy.deepcopy(parent)
                bl.append(copy.deepcopy(self.data.blocks[ident].discoTimestamp))
                parent = self.data.blocks[ident].parent
                count = count-1
            # sort    
            bl = sorted(bl)
            
            # remove outliers
            bl = bl[120:-120]
            
            # get topTime and botTime
            topTime = bl[-1]
            botTime = bl[0]
            
            # Assert algebra will work
            assert 0 <= 960 - count and 960 - count < 961
            assert topTime > botTime
            
            # Sort of the MLE: # blocks/difference in reported times
            # But not the MLE, since the reported times may not be 
            # the actual times, the "difference in reported times" != 
            # "ground truth difference in block discoery times" in general 
            naiveDiscoRate = (960 - count)/(topTime - botTime)
            
            # How much should difficulty change?
            self.diff = self.diff*(naiveDiscoRate/targetRate)
            
        elif mode=="MOM:expModGauss":
            # Similar to "vanSaberhagen" except with 2-minute blocks and
            # we attempt to take into account that "difference in timestamps" 
            # can be negative by:
            # 1) insisting that the ordering induced by the blockchain and
            # 2) modeling timestamps as exponentially modified gaussian.
            # If timestamps are T = X + Z where X is exponentially dist-
            # ributed with parameter lambda and Z is some Gaussian 
            # noise with average mu and variance sigma2, then we can est-
            # imate sigma2, mu, and lambda:
            #       mu     ~ mean - stdev*(skewness/2)**(1.0/3.0)
            #       sigma2 ~ variance*(1-(skewness/2)**(2.0/3.0))
            #       lambda ~ (1.0/(stdev))*(2/skewness)**(1.0/3.0)
            assert targetRate==1.0/120.0
            count = 1200
            ident = self.data.miningIdent
            bl = []
            bl.append(copy.deepcopy(self.data.blocks[ident].discoTimestamp))
            parent = self.data.blocks[ident].parent
            count = count - 1
            while count > 0 and parent is not NOne:
                ident = copy.deepcopy(parent)
                bl.append(copy.deepcopy(self.data.blocks[ident].discoTimestamp))
                parent = self.data.blocks[ident].parent
                count = count-1
            sk   = skew(bl)
            va   = var(bl)
            stdv = sqrt(va)
            lam  = (1.0/stdv)*(2.0/sk)**(1.0/3.0)
            self.diff = self.diff*(lam/targetRate)
        else:
            print("Error, invalid difficulty mode entered.")
            
    def propagate(self, blockIdent):
        for edgeIdent in self.edges:
            e = self.edges[edgeIdent]
            l = e.data["length"]
            toa = self.t + l
            mIdent = e.getNeighbor(n.ident)
            m = e.nodes[mIdent]
            if blockIdent not in m.data["blockchain"]:
                pB = e.data["pendingBlocks"]
                pendingIdent = newIdent(len(pB))
                pendingDat = {"timeOfArrival":toa, "destIdent":mIdent, "block":self.blocks[blockIdent]}
                pB.update({pendingIdent:pendingDat})
       

class Test_Node(unittest.TestCase):
    def test_node(self):
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
        
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_Blockchain)
unittest.TextTestRunner(verbosity=1).run(suite)
             
                
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

class Graph(object):
    '''
    Graph object. Contains some data, a dict of nodes, and a dict of edges.
    '''
    def __init__(self, params={}, verbosity=True):
        self.data=params
        self.verbose = verbosity
        self.nodes = {}
        self.edges = {}
        
    def createGraph(self, numNodes, probEdge, maxNeighbors):
        # Create a new random graph with numNodes nodes, a
        # likelihood any unordered pair of vertices has an edge
        # probEdge, and maximum number of neighbors per node
        # maxNeighbors.
        
        # First, include inputted information into self.data
        self.data.update({"probEdge":probEdge, "maxNeighbors":maxNeighbors})
        
        # Next, for each node to be added, create the node and name it.
        for i in range(numNodes):
            nIdent = newIdent(i)
            bl = Blockchain([], verbosity=True)
            dat = {"blockchain":bl, "intensity":newIntensity(["uniform"]), "offset":newOffset("sumOfSkellams")}
            # A node needs an ident, a data object, a verbosity, and a difficulty
            n = Node([nIdent, dat, self.verbose, 1.0])
            self.nodes.update({n.ident:n})
             
        # Next, for each possible node pair, decide if an edge exists.
        touched = {} # Dummy list of node pairs we have already considered.
        for nIdent in self.nodes:
            n = self.nodes[nIdent] # Pick a node
            for mIdent in self.nodes:
                m = self.nodes[mIdent] # Pick a pair element
                notSameNode = (nIdent != mIdent) # Ensure we aren't dealing with (x,x)
                nOpenSlots = (len(n.edges) < self.data["maxNeighbors"]) # ensure both nodes have open slots available for new edges
                mOpenSlots = (len(m.edges) < self.data["maxNeighbors"])
                untouched = ((nIdent, mIdent) not in touched) # make sure the pair and its transposition have not been touched
                dehcuotnu = ((mIdent, nIdent) not in touched)
                if notSameNode and nOpenSlots and mOpenSlots and untouched and dehcuotnu:
                    # Mark pair as touhed
                    touched.update({(nIdent,mIdent):True, (mIdent,nIdent):True})
                    if random.random() < self.data["probEdge"]:
                        # Determine if edge should exist and if so, add it.
                        nonce = len(self.edges)
                        e = Edge([newIdent(nonce),{"length":random.random(), "pendingBlocks":[]},self.verbose])
                        e.nodes.update({n.ident:n, m.ident:m})
                        self.nodes[nIdent].edges.update({e.ident:e})
                        self.nodes[mIdent].edges.update({e.ident:e})
                        self.edges.update({e.ident:e})
                        
    def addNode(self):
        # Add new node
        n = Node([self.newIdent(len(self.nodes)), {}, self.verbose, 1.0])
        self.nodes.update({n.ident:n})
        for mIdent in self.nodes:
            # For every other node, check if an edge should exist and if so add it.
            m = self.nodes[mIdent]
            notSameNode = (n.ident != mIdent)
            nOpenSlots = (len(n.edges) < self.data["maxNeighbors"])
            mOpenSlots = (len(m.edges) < self.data["maxNeighbors"])
            if notSameNode and nOpenSlots and mOpenSlots and random.random() < self.data["probEdge"]:
                nonce = len(self.edges)
                e = Edge([self.newIdent(nonce), {"length":random.random(), "pendingBlocks":[]}, self.verbose])
                e.nodes.update({n.ident:n, m.ident:m})
                n.edges.update({e.ident:e})
                self.nodes[mIdent].edges.update({e.ident:e})
                self.edges.update({e.ident:e})
        return n.ident
                
    def delNode(self, ident):
        # Remove a node and wipe all memory of its edges from history.
        edgesToDelete = self.nodes[ident].edges
        for edgeIdent in edgesToDelete:
            e = edgesToDelete[edgeIdent]
            otherIdent = e.getNeighbor(ident)
            del self.edges[edgeIdent]
            del self.nodes[otherIdent].edges[edgeIdent]
        del self.nodes[ident]
    
class Test_Graph(unittest.TestCase):
    def test_graph(self):
        greg = Graph()
        greg.createGraph(3, 0.5, 10)
        self.assertEqual(len(greg.nodes),3)
        greg.addNode()
        self.assertEqual(len(greg.nodes),4)
        for edge in greg.edges:
            self.assertEqual(len(greg.edges[edge].nodes),2)
        nodeToKill = random.choice(list(greg.nodes.keys()))
        greg.delNode(nodeToKill)
        for edge in greg.edges:
            self.assertEqual(len(greg.edges[edge].nodes),2)
            for nodeIdent in greg.edges[edge].nodes:
                self.assertTrue(nodeIdent in greg.nodes)
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_Graph)
unittest.TextTestRunner(verbosity=1).run(suite)
        
class FishGraph(StochasticProcess):
    '''
    Stochastic process on a graph 
    with the graph growing in a stochastic process too
    '''
    # TODO: Check if output.txt exists before beginning. If so, clear it and create a new one.
    # TODO: Instead of/in addition to storing graph data in a text file, can we plot with ggplot in R?
    def __init__(self, params=None, verbosity=True):
        # Initialize
        
        assert "maxTime" in params
        self.maxTime = copy.deepcopy(params["maxTime"])
        del params["maxTime"]
        
        assert "numNodes" in params
        numNodes = params["numNodes"]
        del params["numNodes"]
        
        self.data = params
        self.t = 0.0
        self.state = Graph()
        self.filename = "output.txt"
        self.verbose = verbosity
        
        # Create graph
        self.state.createGraph(numNodes, self.data["probEdge"], self.data["maxNeighbors"])
        
        # Update node data
        for nIdent in self.state.nodes:
            n = self.state.nodes[nIdent]
            difficulty = 1.0
            intensity = newIntensity(params="uniform")
            offset = newOffset(params="sumOfSkellams")
            dat = {"intensity":intensity, "offset":offset, "blockchain":Blockchain([], verbosity=self.verbose)}
            n.data.update(dat)
            
        # Update edge data.
        for eIdent in self.state.edges:
            e = self.state.edges[eIdent]
            e.data.update({"pendingBlocks":{}})
        
    def go(self):
        assert self.maxTime > 0.0
        while self.t <= self.maxTime and len(self.state.nodes) > 0:
            deltaT = self.getNextTime()
            self.updateState(self.t, deltaT)
            self.record()
            
    def getNextTime(self):
        # Each Poisson process event generates an exponential random variable.
        # The smallest of these is selected
        # The rate of the smallest determines event type.
        eventTag = None
        
        u = 0.0
        while(u == 0.0):
            u = copy.deepcopy(random.random())
        u = -1.0*math.log(copy.deepcopy(u))/self.data["birthRate"] # Time until next stochastic birth
        eventTag = "birth"
        
        v = 0.0
        while(v == 0.0):
            v = copy.deepcopy(random.random())
        v = -1.0*math.log(copy.deepcopy(v))/self.data["deathRate"] # Time until next stochastic death
        if v < u:
            u = copy.deepcopy(v)
            eventTag = "death"
            
        for nIdent in self.state.nodes:
            n = self.state.nodes[nIdent] # n.ident = nIdent 
            v = 0.0
            while(v == 0.0):
                v = copy.deepcopy(random.random())
            v = -1.0*math.log(copy.deepcopy(v))/n.data["intensity"]
            if v < u:
                u = copy.deepcopy(v)
                eventTag = ["discovery", n.ident]
                
        # Now that all the STOCHASTIC arrivals have been decided,
        # We check if any of the deterministic events fire off instead.
        for eIdent in self.state.edges:
            e = self.state.edges[eIdent] # e.ident = eIdent
            pB = e.data["pendingBlocks"]
            if len(pB) > 0:
                for pendingIdent in pB:
                    arrivalInfo = pB[pendingIdent]
                    v = arrivalInfo["timeOfArrival"] - self.t
                    if v < u and 0.0 < v:
                        u = copy.deepcopy(v)
                        eventTag = ["arrival", e.ident, pendingIdent]
                        
        deltaT = (u, eventTag)
        # Formats:
        #   eventTag = ["arrival", e.ident, pendingIdent]
        #   eventTag = ["discovery", n.ident]
        #   eventTag = "death"
        #   eventTag = "birth"
        return deltaT
        
    def updateState(self, t, deltaT, mode="Nakamoto", targetRate=1.0/1209600.0):
        # Depending on eventTag, update the state...
        u = deltaT[0]
        shout = ""
        eventTag = deltaT[1]
        
        if type(eventTag)==type("birthordeath"):
            if eventTag == "death":
                # Picks random nodeIdent and kills it
                toDie = random.choice(list(self.state.nodes.keys()))
                x = len(self.state.nodes)
                shout += "DEATH, Pop(Old)=" + str(x) + ", Pop(New)="
                if self.verbose:
                    print(shout)
                self.state.delNode(toDie)
                y = len(self.state.nodes)
                assert y == x - 1
                shout += str(y) + "\n"
                
            elif eventTag == "birth":
                # Adds node with some randomly determined edges
                x = len(self.state.nodes)
                shout += "BIRTH, Pop(Old)=" + str(x) + ", Pop(New)="
                if self.verbose:
                    print(shout)
                nIdent = self.state.addNode() 
                n = self.state.nodes[nIdent]
                intensity = random.random()/1000.0
                offset = 2.0*random.random() - 1.0
                n.data.update({"intensity":intensity, "offset":offset, "blockchain":{}})
                # Auto syncs new node.
                for eIdent in n.edges:
                    e = n.edges[eIdent]
                    e.data.update({"pendingBlocks":{}})
                    mIdent = e.getNeighbor(n.ident)
                    m = self.state.nodes[mIdent]
                    mdata = m.data["blockchain"]
                    n.data["blockchain"].update(mdata)
                y = len(self.state.nodes)
                assert y == x + 1
                shout += str(y) + "\n"
            else:
                print("Error: eventTag had length 1 but was neighter a birth or a death, this shouldn't happen so this else case will eventually be removed, I guess? Our eventTag = ", eventTag)
        elif len(eventTag)==2:
            # Block is discovered and plunked into each edge's pendingBlock list.
            
            shout += "DISCOVERY"
            if self.verbose:
                print(shout)
                
            assert eventTag[0]=="discovery"
            assert eventTag[1] in self.state.nodes
            nIdent = eventTag[1] # get founding node's identity
            n = self.state.nodes[nIdent] # get founding node
            s = self.t + n.data["offset"] # get founding node's wall clock
            
            newBlockIdent = newIdent(len(n.data["blockchain"].blocks)) # generate new identity
            disco = s
            arriv = s
            parent = n.data["blockchain"].miningIdent
            diff = copy.deepcopy(n.diff)
            verbosity = self.verbose
            
            newBlock = Block([newBlockIdent, disco, arriv, parent, diff, verbosity])
            n.updateBlockchain({newBlockIdent:newBlock})
            n.updateDifficulty(mode, targetRate)
            n.propagate(newBlockIdent)
            
        elif len(eventTag)==3: 
            #eventTag = ("arrival", e.ident, pendingIdent)
            # A block deterministically arrives at the end of an edge.
            
            assert eventTag[0]=="arrival"
            shout += "ARRIVAL"
            if self.verbose:
                print(shout)
            
            eIdent = eventTag[1]
            pendingIdent = eventTag[2]
            e = self.state.edges[eIdent]
            pB = e.data["pendingBlocks"]
            arrivalInfo = pB[pendingIdent] # arrivalInfo = {"timeOfArrival":toa, "destIdent":mIdent, "block":newBlock}
            
            assert arrivalInfo["destIdent"] in self.state.nodes
            assert self.t + u == arrivalInfo["timeOfArrival"]
            receiver = self.state.nodes[arrivalInfo["destIdent"]]
            arriv = self.t + u + receiver.data["offset"]
            newBlock = arrivalInfo["block"]
            newBlock.arrivTimestamp = copy.deepcopy(arriv)
            receiver.data["blockchain"].updateBlockchain({newBlock.ident:newBlock})
            receiver.updateDifficulty(mode, targetRate)
            receiver.propagate(newBlock.ident)
            
        else:
            print("Error: eventTag was not a string, or not an array length 2 or 3. In fact, we have eventTag = ", eventTag)
            
        if self.verbose:
            print("u = ", u)
        self.t += u
        if self.verbose:
            print(str(self.t) + "\t" + shout)
        
    def record(self):
        with open(self.filename, "a") as f:
            line = ""
            # Format will be edgeIdent,nodeAident,nodeBident
            line += str("t=" + str(self.t) + ",")
            ordKeyList = sorted(list(self.state.edges.keys()))
            for key in ordKeyList:
                entry = []
                entry.append(key)
                nodeKeyList = sorted(list(self.state.edges[key].nodes))
                for kkey in nodeKeyList:
                    entry.append(kkey)
                line += str(entry) + ","
            f.write(line + "\n")

class Test_FishGraph(unittest.TestCase):
    def test_fishGraph(self):
        for i in range(10):
            params = {"numNodes":10, "probEdge":0.5, "maxNeighbors":10, "maxTime":10.0, "birthRate":0.001, "deathRate":0.001}
            greg = FishGraph(params, verbosity=True)
            greg.go()
            
       
suite = unittest.TestLoader().loadTestsFromTestCase(Test_FishGraph)
unittest.TextTestRunner(verbosity=1).run(suite)
        
        
