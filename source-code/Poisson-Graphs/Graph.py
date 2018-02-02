 from Edge import *

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
        n = Node([newIdent(len(self.nodes)), {}, self.verbose, 1.0])
        self.nodes.update({n.ident:n})
        for mIdent in self.nodes:
            # For every other node, check if an edge should exist and if so add it.
            m = self.nodes[mIdent]
            notSameNode = (n.ident != mIdent)
            nOpenSlots = (len(n.edges) < self.data["maxNeighbors"])
            mOpenSlots = (len(m.edges) < self.data["maxNeighbors"])
            if notSameNode and nOpenSlots and mOpenSlots and random.random() < self.data["probEdge"]:
                nonce = len(self.edges)
                e = Edge([newIdent(nonce), {"length":random.random(), "pendingBlocks":[]}, self.verbose])
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
        
