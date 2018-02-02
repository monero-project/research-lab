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
                    n.updateBlockchain(mdata)
                y = len(self.state.nodes)
                assert y == x + 1
                shout += str(y) + "\n"
            else:
                print("Error: eventTag had length 1 but was neighter a birth or a death, this shouldn't happen so this else case will eventually be removed, I guess? Our eventTag = ", eventTag)
        elif len(eventTag)==2:
            # Block is discovered and plunked into each edge's pendingBlock list.
            
            shout += "DISCOVERY\n"
            if self.verbose:
                print(shout)
                
            if self.verbose:
                print("Checking formation of eventTag = [\"discovery\", nodeIdent]")
            assert eventTag[0]=="discovery"
            assert eventTag[1] in self.state.nodes
            
            if self.verbose:
                print("Retrieving discoverer's identity")
            nIdent = eventTag[1] # get founding node's identity
            
            if self.verbose:
                print("Retrieving discoverer")
            n = self.state.nodes[nIdent] # get founding node
            
            if self.verbose:
                print("Computing discoverer's wall clock")
            s = self.t + n.data["offset"] # get founding node's wall clock
            
            
            if self.verbose:
                print("Generating new block identity")
            newBlockIdent = newIdent(len(n.data["blockchain"].blocks)) # generate new identity
            
            if self.verbose:
                print("Setting timestamps")
            disco = s
            arriv = s
            
            if self.verbose:
                print("Retrieving parent")
            parent = n.data["blockchain"].miningIdent
            
            if self.verbose:
                print("getting difficulty")
            diff = copy.deepcopy(n.diff)
            
            if self.verbose:
                print("setting verbosity")
            verbosity = self.verbose
            
            if self.verbose:
                print("Initializing a new block")
            newBlock = Block([newBlockIdent, disco, arriv, parent, diff, verbosity])
            
            if self.verbose:
                print("Updating discovering node's blockchain")
            n.updateBlockchain({newBlockIdent:newBlock})
            
            if self.verbose:
                print("Computing discoverer's new difficulty")
            n.updateDifficulty(mode, targetRate)
            
            if self.verbose:
                print("propagating new block.")
            n.propagate(self.t, newBlockIdent)
            
            if self.verbose:
                print("discovery complete")
            
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
            receiver.updateBlockchain({newBlock.ident:newBlock})
            receiver.updateDifficulty(mode, targetRate)
            receiver.propagate(self.t, newBlock.ident)
            
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
            params = {"numNodes":10, "probEdge":0.5, "maxNeighbors":10, "maxTime":10.0, "birthRate":0.1, "deathRate":0.1}
            greg = FishGraph(params, verbosity=True)
            greg.go()
            
       
suite = unittest.TestLoader().loadTestsFromTestCase(Test_FishGraph)
unittest.TextTestRunner(verbosity=1).run(suite)
        
        
