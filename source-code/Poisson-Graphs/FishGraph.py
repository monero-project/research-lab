import unittest, copy, random, math

class stochasticProcess(object):
    def __init__(self, params=None):
        self.data = params
        self.t = 0.0
        self.state = 0.0
        self.maxTime = 1000.0
        
    def go(self):
        assert self.maxTime > 0.0
        while self.t <= self.maxTime:
            deltaT = self.getNextTime()
            self.updateState(deltaT)
            #print(str(self.t) + ", " + str(self.state))
            
    def getNextTime(self):
        return 1
        
    def updateState(self, deltaT):
        self.state += random.randrange(-1,2,1) # [-1, 0, 1]
        self.t += deltaT
    
	
class Test_stochasticProcess(unittest.TestCase):
    def test_sp(self):
        sally = stochasticProcess()
        sally.go()
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_stochasticProcess)
unittest.TextTestRunner(verbosity=1).run(suite)

class Node(object):
    def __init__(self, params=["", {}]):
        self.ident = params[0]
        self.data = params[1]
        self.edges = {}
        
class Edge(object):
    def __init__(self, params=["", {}]):
        self.ident = params[0]
        self.data = params[1]
        self.nodes = {}
        
    def getNeighbor(self, nodeIdent):
        result = nodeIdent in self.nodes
        if result:
            for otherIdent in self.nodes:
                if otherIdent != nodeIdent:
                    result = otherIdent
        return result

class Graph(object):
    def __init__(self, params={}):
        self.data=params
        self.nodes = {}
        self.edges = {}
    def newIdent(self, nonce):
        return hash(str(nonce) + str(random.random()))
    def createGraph(self, numNodes, probEdge, maxNeighbors):
        self.data.update({"numNodes":numNodes, "probEdge":probEdge, "maxNeighbors":maxNeighbors})
        for i in range(numNodes):
            nIdent = self.newIdent(i)
            n = Node([nIdent,{}])
            self.nodes.update({n.ident:n})
        touched = {}
        for nIdent in self.nodes:
            n = self.nodes[nIdent]
            for mIdent in self.nodes:
                m = self.nodes[mIdent]
                notSameNode = (nIdent != mIdent)
                nOpenSlots = (len(n.edges) < self.data["maxNeighbors"])
                mOpenSlots = (len(m.edges) < self.data["maxNeighbors"])
                untouched = ((nIdent, mIdent) not in touched)
                dehcuotnu = ((mIdent, nIdent) not in touched)
                if notSameNode and nOpenSlots and mOpenSlots and untouched and dehcuotnu:
                    touched.update({(nIdent,mIdent):True, (mIdent,nIdent):True})
                    if random.random() < self.data["probEdge"]:
                        nonce = len(self.edges)
                        e = Edge([self.newIdent(nonce),{"length":random.random(), "pendingBlocks":[]}])
                        e.nodes.update({n.ident:n, m.ident:m})
                        self.nodes[nIdent].edges.update({e.ident:e})
                        self.nodes[mIdent].edges.update({e.ident:e})
                        self.edges.update({e.ident:e})
    def addNode(self):
        n = Node([self.newIdent(len(self.nodes)), {}])
        self.nodes.update({n.ident:n})
        for mIdent in self.nodes:
            m = self.nodes[mIdent]
            notSameNode = (n.ident != mIdent)
            nOpenSlots = (len(n.edges) < self.data["maxNeighbors"])
            mOpenSlots = (len(m.edges) < self.data["maxNeighbors"])
            if notSameNode and nOpenSlots and mOpenSlots and random.random() < self.data["probEdge"]:
                nonce = len(self.edges)
                e = Edge([self.newIdent(nonce), {"length":random.random(), "pendingBlocks":[]}])
                e.nodes.update({n.ident:n, m.ident:m})
                n.edges.update({e.ident:e})
                self.nodes[mIdent].edges.update({e.ident:e})
                self.edges.update({e.ident:e})
        return n.ident
                
    def delNode(self, ident):
        edgesToDelete = self.nodes[ident].edges
        for edgeIdent in edgesToDelete:
            if edgeIdent in self.edges:
                del self.edges[edgeIdent]
        del self.nodes[ident]
    
class Test_Graph(unittest.TestCase):
    def test_graph(self):
        greg = Graph()
        greg.createGraph(3, 0.5, 10)
        self.assertEqual(len(greg.nodes),3)
        for edge in greg.edges:
            print(greg.edges[edge].ident, "\t", [greg.edges[edge].nodes[n].ident for n in greg.edges[edge].nodes], "\n")
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
        





class FishGraph(stochasticProcess):
    def __init__(self, params=None):
        self.data = params
        self.t = 0.0
        self.state = Graph()
        self.state.createGraph(self.data["numNodes"], self.data["probEdge"], self.data["maxNeighbors"])
        for nIdent in self.state.nodes:
            n = self.state.nodes[nIdent]
            difficulty = 10000.0
            intensity = random.random()/difficulty
            offset = 2.0*random.random() - 1.0
            n.data.update({"intensity":intensity, "offset":offset, "blockchain":{}})
        for eIdent in self.state.edges:
            e = self.state.edges[eIdent]
            e.data.update({"pendingBlocks":[]})
        self.maxTime = self.data["maxTime"]
        
    def go(self):
        assert self.maxTime > 0.0
        while self.t <= self.maxTime and len(self.state.nodes) > 0:
            deltaT = self.getNextTime()
            self.updateState(deltaT)
            #print(str(self.t) + ", " + str(self.state))
            
    def getNextTime(self):
        eventTag = None
        
        u = copy.deepcopy(random.random())
        u = -1.0*math.log(copy.deepcopy(u))/self.data["birthRate"] # Time until next stochastic birth
        eventTag = "birth"
        
        v = copy.deepcopy(random.random())
        v = -1.0*math.log(copy.deepcopy(v))/self.data["deathRate"] # Time until next stochastic death
        if v < u:
            u = copy.deepcopy(v)
            eventTag = "death"
            
        for nIdent in self.state.nodes:
            n = self.state.nodes[nIdent] # n.ident = nIdent 
            v = copy.deepcopy(random.random())
            v = -1.0*math.log(copy.deepcopy(v))/n.data["intensity"]
            if v < u:
                u = copy.deepcopy(v)
                eventTag = ["discovery", n.ident]
                
        for eIdent in self.state.edges:
            e = self.state.edges[eIdent] # e.ident = eIdent
            bufferedBlocks = e.data["pendingBlocks"]
            if len(bufferedBlocks) > 0:
                for pendingIdent in bufferedBlocks:
                    pB = bufferedBlocks[pendingIdent]
                    v = pB["timeOfArrival"]
                    if v < u:
                        u = copy.deepcopy(v)
                        eventTag = ["arrival", e.ident, pendingIdent]
                        
        deltaT = (u, eventTag)
        # eventTag = ["arrival", e.ident, pendingIdent]
        # eventTag = ["discovery", n.ident]
        # eventTag = "death"
        # eventTag = "birth"
        return deltaT
        
    def updateState(self, deltaT):
        u = deltaT[0]
        eventTag = deltaT[1]
        
        if type(eventTag)==type("birthordeath"):
            if eventTag == "death":
                # Picks random nodeIdent and kills it
                toDie = random.choice(list(self.state.nodes.keys()))
                print("DEATH EVENT:")
                print("Pre-death population = ", len(self.state.nodes))
                self.state.delNode(toDie)
                print("Post-death population = ", len(self.state.nodes))
                print("Done. \n")
                
            elif eventTag == "birth":
                # Adds node with some randomly determined edges
                print("BIRTH EVENT:")
                print("Pre-birth population = ", len(self.state.nodes))
                nIdent = self.state.addNode() 
                print("Post-death population = ", len(self.state.nodes))
                n = self.state.nodes[nIdent]
                intensity = random.random()/10000.0
                offset = 2.0*random.random() - 1.0
                n.data.update({"intensity":intensity, "offset":offset, "blockchain":{}})
                # Auto syncs new node.
                print("Auto syncing new node...")
                for eIdent in n.edges:
                    e = n.edges[eIdent]
                    e.data.update({"pendingBlocks":[]})
                    mIdent = e.getNeighbor(n.ident)
                    m = self.state.nodes[mIdent]
                    mdata = m.data["blockchain"]
                    n.data["blockchain"].update(mdata)
                print("Done. \n")
            else:
                print("Error: eventTag had length 1 but was neighter a birth or a death. We had ", eventTag)
        elif len(eventTag)==2:
            assert eventTag[0]=="discovery"
            nIdent = eventTag[1]
            n = self.state.nodes[n]
            s = self.t + n.data["offset"]
            n.data["blockchain"].append(s)
            for edgeIdent in n.edges:
                e = n.edges[edgeIdent]
                l = e.data["length"]
                toa = self.t + l
                mIdent = e.getNeighbor(n.ident)
                e.data["pendingBlocks"].append({"timestamp":s, "timeOfArrival":toa, "destIdent":mIdent})
            print("Block Discovery event. To be coded. For now, blah blah.")
        elif len(eventTag)==3:
            assert eventTag[0]=="arrival"
            print("Block Arrival event. To be coded. For now, blah blah.")
        else:
            print("Error: eventTag was not a string, or not an array length 2 or 3. In fact, we have eventTag = ", eventTag)
            
            

class Test_FishGraph(unittest.TestCase):
    def test_fishGraph(self):
        params = {"numNodes":10, "probEdge":0.5, "maxNeighbors":10, "maxTime":100.0, "birthRate":1.1, "deathRate":0.2}
        greg = FishGraph(params)
        greg.go()
        
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_FishGraph)
unittest.TextTestRunner(verbosity=1).run(suite)
        
        
