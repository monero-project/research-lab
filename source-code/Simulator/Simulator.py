import copy, hashlib, time

class Event(object):
    ''' Generalized event object '''
    def __init__(self,params):
        self.data = {}
        self.timeOfEvent = None
        self.eventType = None


class Block(object):
    ''' Block object, very simple... has an identity and a timestamp'''
    def __init__(self, params):
        self.ident = params[0]
        self.timestamp = params[1]

class Node(object):
    '''
    Node object, represents a computer on the network.
    Has an identity, a dict (?) of edges, a time offset on [-1,1]
    representing how inaccurate the node's wall clock appears to be,
    an intensity representing the node's hash rate, a blockchain
    which is merely a list of block objects (ordered by their arrival
    at the node, for simplicity), and a difficulty score (which is
    a function of the blockchain)
    '''
    def __init__(self, params):
        self.ident      = params[0] # string
        self.edges      = params[1] # dict of edges
        self.timeOffset = params[2] # float
        self.intensity  = params[3] # float (positive)
        self.difficulty = params[4]
        self.blockchain = []
        
    def makeBlock(self, t):
        ts = t + self.timeOffset
        newBlock = Block()
        salt = random.random()
        n = len(self.blockchain)
        x = hash(str(n) + str(salt))
        newBlock.ident = x
        newBlock.timestamp = ts
        self.blockchain.append(newBlock)
        self.computeDifficulty()
        return newBlock
        
    # node object needs receiveBlock(block) method
    def receiveBlock(self, blockToReceive):
        self.blockchain.append(blockToReceive)
        
    def computeDifficulty(self, target, sampleSize):
        N = min(sampleSize,len(self.blockchain))
        tempSum = 0.0
        for i in range(N):
            tempSum += abs(self.blockchain[-i].timestamp - self.blockchain[-i-1].timestamp)
        tempSum = float(tempSum)/float(N) # Average absolute time difference of last N blocks
        lambdaMLE = 1.0/tempSum
        self.difficulty = float(lambdaMLE/target)*self.difficulty
        
class Edge(object):
    '''
    Edge object representing the connection between one node and another.
    Has two node objects, a and b, a length l, and a dictionary of pending blocks.
    '''
    def __init__(self, params):
        self.ident = params[0] # edge ident
        self.a = params[1] # node ident of one incident node
        self.b = params[2] # node ident of the other incident node (may be None when creating new blocks?)
        self.l = params[3] # length of edge as measured in propagation time.
        self.pendingBlocks = {} # blockIdent:(block, destination node ident, deterministic time of arrival)
        
    def addBlock(self, blockToAdd, blockFinderIdent, curTime):
        # Include new block to self.pendingBlocks
        timeOfArrival = curTime + self.l
        if blockFinderIdent == self.a.ident:
            self.pendingBlocks.update({blockToAdd.ident:(blockToAdd, self.b.ident, timeOfArrival)})
        elif blockFinderIdent == self.b.ident:
            self.pendingBlocks.update({blockToAdd.ident:(blockToAdd, self.a.ident, timeOfArrival)})
        else:
            print("fish sticks.")
        

class Network(object):
    '''
    Network object consisting of a number of vertices, a probability that any pair of vertices
    has an edge between them, a death rate of vertices, a dictionary of vertices, a dictionary
    of edges, and a clock t.
    '''
    def __init__(self, params):
        self.numVertices    = params[0] # integer
        self.probOfEdge     = params[1] # float (between 0.0 and 1.0)
        self.deathRate      = params[2] # float 1.0/(avg vertex lifespan)
        self.vertices       = {} # Dict with keys=node idents and values=nodes
        self.edges          = {} # Dict with keys=edge idents and values=edges
        self.t              = 0.0
        self.defaultNodeLength = 30.0 # milliseconds
        self.initialize()
        
    def initialize(self):
        # Generate self.numVertices new nodes with probability self.probOfEdge
        # that any pair are incident. Discard any disconnected nodes (unless
        # there is only one node)
        try:
            assert self.numVertices > 1
        except AssertionError:
            print("Fish sticks... AGAIN! Come ON, fellas!")
            
        count = self.numVertices - 1
        
        e = Event()
        e.eventType = "node birth"
        e.timeOfEvent = 0.0
        e.data = {"neighbors":[]}
        self.birthNode(e)
        
        while count > 0:
            count -= 1
            e.eventType = "node birth"
            e.timeOfEvent = 0.0
            e.data = {"neighbors":[]}
            for x in self.vertices:
                u = random.random()
                if u < self.probOfEdge:
                    e.data["neighbors"].append(x)
            self.birthNode(e)
    
    def run(self, maxTime, birthrate=lambda x:math.exp(-(x-10.0)**2.0)):
        # Run the simulation for maxTime and birthrate function (of time)
        while self.t < maxTime:
            if type(birthrate) is float: # We may pass in a constant birthrate
                birthrate = lambda x:birthrate # but we want it treated as a function
            e = self.nextEvent(birthrate) # Generate next event.
            try:
                assert e is not None
            except AssertionError:
                print("Got null event in run, bailing...")
                break
            self.t = e.timeOfEvent # Get time until next event.
            self.execute(e) # Run the execute method
            
    def nextEvent(self, birthrate, t):
        # The whole network experiences stochastic birth and death as a Poisson
        # process, each node experiences stochastic block discovery as a (non-
        # homogeneous) Poisson process. Betwixt these arrivals, other
        # deterministic events occur as blocks are propagated along edges,
        # changing the (local) block discovery rates.
        
        # Birth of node?
        u = random.random()
        u = math.ln(1.0-u)/birthrate(t)
        e = Event()
        e.eventType = "node birth"
        e.timeOfEvent = self.t + u
        e.data = {"neighbors":[]}
        for x in self.vertices:
            u = random.random()
            if u < self.probOfEdge:
                e.data["neighbors"].append(x)
        
        for x in self.vertices:
            u = random.random()
            u = math.ln(1.0 - u)/self.deathRate
            tempTime = self.t + u
            if tempTime < e.timeOfEvent:
                e.eventType = "node death"
                e.timeOfEvent = tempTime
                e.data = {"identToKill":x}
                
            u = random.random()
            localIntensity = self.vertices[x].intensity/self.vertices[x].difficulty
            u = math.ln(1.0 - u)/localIntensity
            tempTime = self.t + u
            if tempTime < e.timeOfEvent:
                e.eventType = "block found"
                e.timeOfEvent = tempTime
                e.data = {"blockFinderIdent":x}

            for edgeIdent in self.vertices[x].edges:
                for pendingBlockIdent in self.edges[edgeIdent]:
                    timeOfBlockArrival = self.edges[edgeIdent].pendingBlocks[pendingBlockIdent][2]
                    if timeOfBlockArrival < e.timeOfEvent:
                        e.eventType = "block propagated"
                        e.timeOfEvent = timeOfBlockArrival
                        e.data = {"propEdgeIdent":edgeIdent, "pendingBlockIdent":blockIdent}
        return e
            
    def execute(self, e):
        # Take an event e as input. Depending on eventType of e, execute
        # the correspondsing method.
        if e.eventType == "node birth":
            self.birthNode(e)
        elif e.eventType == "node death":
            self.killNode(e)
        elif e.eventType == "block found":
            self.foundBlock(e)
        elif e.eventType == "block propagated":
            self.propBlock(e)
            
    def birthNode(self, e):
        # In this event, a new node is added to the network and edges are randomly decided upon.
        # I will probably limit the number of peers for a new node eventually: a fixed probability
        # of even 1% of edges per pair of nodes, in a graph with, say 1000 nodes, will see 10 peers
        # per node...
        # Also, I was kind of thinking this code should probably run with less than 50 nodes at a time, in general,
        # otherwise the simulation needs to be highly optimized to make for reasonable simulation times.

        newNodeIdent = hash(str(len(self.vertices)) + str(random.random())) # Pick a new random node ident
        newOffset = 2.0*random.random() - 1.0 # New time offset for the new node
        newIntensity = random.random() # New node hash rate
        newDifficulty = 1.0 # Dummy variable, will be replaced

        newbc = [] # This will be the union of the blockchains of all neighbors in e.data["neighbors"]
        count = 0 # This will be a nonce to be combined with a salt for a unique identifier
        newEdges = {}
        for neighborIdent in e.data["neighbors"]:
            newbc += [z for z in self.vertices[neighborIdent].blockchain if z not in newbc]
            newEdgeIdent = hash(str(count) + str(random.random()))
            count += 1
            newLength = random.random()*self.defaultNodeLength
            otherSide = random.choice(self.vertices.keys())
            newEdge = Edge([newEdgeIdent, newNodeIdent, otherSide, newLength])
            newEdges.update({newEdgeIdent:newEdge})

        params = [newNodeIdent, newEdges, newOffset, newIntensity, newDifficulty]
        newNode = Node(params) # Create new node
        newNode.blockchain = newbc # Store new blockchain
        newNode.computeDifficulty() # Compute new node's difficulty
        
        self.vertices.update({newIdent:newNode}) # Add new node to self.vertices
        self.edges.update(newEdges) # Add all new edges to self.edges
        
    def killNode(self, e):
        # Remove node and all incident edges
        nodeIdentToKill = e.data["identToKill"]
        #edgesToKill = e.data["edgesToKill"]
        for edgeIdentToKill in self.vertices[nodeIdentToKill].edges:
            del self.edges[edgeIdentToKill]
        del self.vertices[nodeIdentToKill]
            
    def foundBlock(self, e):
        # In this instance, a node found a new block.
        blockFinderIdent = e.data["blockFinderIdent"] # get identity of node that found the block.
        blockFound = self.vertices[blockFinderIdent].makeBlock() # Nodes need a makeBlock method
        for nextEdge in self.vertices[blockFinderIdent].edges: # propagate to edges
            self.edges[nextEdge].addBlock(blockFound, blockFinderIdent, self.t) # Edges need an addBlock method
        
    def propBlock(self, e):
        # In this instance, a block on an edge is plunked onto its destination node and then
        # propagated to the resulting edges.
        propEdgeIdent = e.data["propEdgeIdent"] # get the identity of the edge along which the block was propagating
        blockToPropIdent = e.data["blockIdent"] # get the identity of the block beign propagated
        # Get the block being propagated and the node identity of the receiver.
        (blockToAdd, destIdent) = self.edges[propEdgeIdent].pendingBlocks[blockToPropIdent]
        self.vertices[destIdent].receiveBlock(blockToAdd) # Call receiveBlock from the destination node.
        del self.edges[propEdgeIdent].pendingBlocks[blockToPropIdent] # Now that the block has been received
        for nextEdge in self.vertices[destIdent].edges:
            if nextEdge != propEdgeIdent:
                if self.edges[nextEdge].a.ident == destIdent:
                    otherSideIdent = self.edges[nextEdge].b.ident
                elif self.edges[nextEdge].b.ident == destIdent:
                    otherSideIdent = self.edges[nextEdge].a.ident
                else:
                    print("awww fish sticks, fellas")
                    
                if blockToAdd.ident not in self.vertices[otherSideIdent].blockchain:
                    self.edges[nextEdge].addBlock(blockToAdd, destIdent, self.t)
                    
class Simulator(object):
    def __init__(self, params):
        #todo lol cryptonote style
        pass
    
    def go(self):
        nelly = Network([43, 0.25, 1.0/150.0])
        self.run(maxTime, birthrate=lambda x:math.exp((-(x-500.0)**2.0))/(2.0*150.0))
