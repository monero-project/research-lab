from Blockchain import *
from Node import *
from Edge import *
from copy import *

def newIntensity(params):
    x = random.random()
    return x
    
def newOffset(params):
    x = 2.0*random.random() - 1.0
    return x
    
class Graph(object):
    '''
    Explanation
    '''
    def __init__(self, params):
        self.nodes = {}
        self.edges = {}
        self.mode = params[0]
        self.targetRate = params[1]
        self.numInitNodes = params[2]
        self.maxNeighbors = params[3]
        self.probEdge = params[4]
        self.verbosity = params[5]
        self.startTime = deepcopy(time.time())
        self.runTime = params[6]
        self.globalTime = deepcopy(self.startTime)
        self.birthRate = params[7]
        self.deathRate = params[8]
        self.data = params[9] 
        
        self.blankBlockchain = Blockchain()
        self.blankBlockchain.targetRate = self.data["targetRate"]
        self.blankBlockchain.mode = self.data["mode"]
        
        self._createInit()
        
        
    def _createInit(self):
        # For simplicity, all nodes will have a genesis block with t=0.0 and no offset
        for i in range(self.numInitNodes):
            offset = newOffset()
            intens = newIntensity()
            name = newIdent(len(self.nodes))
            dat = {"offset":offset, "intensity":intens, "blockchain":deepcopy(self.blankBlockchain)}
            params = {"ident":name, "data":dat, "verbose":self.verbosity, "mode":self.mode, "targetRate":self.targetRate}
            nelly = Node(params)
            self.nodes.update({nelly.ident:nelly})
            t = self.startTime
            self.nodes[nelly.ident].generateBlock(t, i)
            
        touched = {}
        for xNode in self.nodes:
            for yNode in self.nodes:
                notSameNode = (xNode != yNode)
                xNodeHasRoom = (len(self.nodes[xNode].edges) < self.maxNeighbors)
                yNodeHasRoom = (len(self.ndoes[yNode].edges) < self.maxNeighbors)
                xyNotTouched = ((xNode, yNode) not in touched)
                yxNotTouched = ((yNode, xNode) not in touched)
                if notSameNode and xNodeHasRoom and yNodeHasRoom and xyNotTouched and yxNotTouched:
                    touched.update({(xNode,yNode):True, (yNode,xNode):True})
                    if random.random() < self.probEdge:
                        params = [newIdent(len(self.edges)), {}, self.verbosity]
                        ed = Edge(params)
                        ed.nodes.update({xNode:self.nodes[xNode], yNode:self.nodes[yNode]})
                        self.edges.update({ed.ident:ed})
                        self.nodes[xNode].edges.update({ed.ident:ed})
                        self.nodes[yNode].edges.update({ed.ident:ed})
        
    def eventNodeJoins(self, t):
        # timestamp,nodeJoins,numberNeighbors,neighbor1.ident,edge1.ident,neighbor2.ident,edge2.ident,...,
        out = ""
        neighbors = []
        for xNode in self.nodes:
            xNodeHasRoom = (len(self.nodes[xNode].edges) < self.maxNeighbors)
            iStillHasRoom = (len(neighbors) < self.maxNeighbors)
            if xNodeHasRoom and and iStillHasRoom and random.random() < self.probEdge:
                neighbors.append(xNode)
                
        
        newNodeName = newIdent(len(self.nodes))
        offset = newOffset()
        intens = newIntensity()
        dat = {"offset":offset, "intensity":intens, "blockchain":deepcopy(self.blankBlockchain)}
        params = {"ident":newNodeName, "data":dat, "verbose":self.verbosity, "mode":self.mode, "targetRate":self.targetRate}
        newNode = Node(params)
        self.nodes.update({newNode.ident:newNode})
        self.nodes[newNode.ident].generateBlock(self.startTime, 0)
        
        out = str(t) + ",nodeJoins," + str(newNode.ident) + "," + str(len(neighbors)) + ","
        for neighbor in neighbors:
            out += neighbor + ","
            params = [newIdent(len(self.edges)), {}, self.verbosity]
            ed = Edge(params)
            ed.nodes.update({neighbor:self.nodes[neighbor], newNode.ident:self.nodes[newNode.ident]})
            out += ed.ident + ","
            self.edges.update({ed.ident:ed})
            self.nodes[neighbor].edges.update({ed.ident:ed})
            self.nodes[newNode.ident].edges.update({ed.ident:ed})
        return out
           
    def eventNodeLeaves(self, t):
        out = str(t) + ",nodeLeaves,"
        leaverIdent = random.choice(list(self.nodes.keys()))
        out += str(leaverIdent) + ","
        leaver = self.nodes[leaverIdent]
        neighbors = []
        for ed in leaver.edges:
            neighbors.append((ed.Ident, ed.getNeighbor(leaverIdent)))
        for neighbor in neighbors:
            edIdent = neighbor[0]
            neiIdent = neighbor[1]
            del self.nodes[neiIdent].edges[edIdent]
            del self.edges[edIdent]
        del self.nodes[leaverIdent]
        return out
        
        
    def eventBlockDiscovery(self, discoIdent, t):
        out = str(t) + ",blockDisco," + str(discoIdent) + ","
        blockIdent = self.nodes[discoIdent].generateBlock(t)
        out += str(blockIdent)
        self.nodes[discoIdent].propagate(t, blockIdent)
        return out
        
    def eventBlockArrival(self, destNodeIdent, edgeIdent, blockIdent, t):
        out = str(t) + ",blockArriv," + str(destNodeIdent) + "," + str(edgeIdent) + "," + str(blockIdent) + ","
        destNode = self.nodes[destNodeIdent]
        edge = self.edges[edgeIdent]
        block = deepcopy(edge.data["pendingBlocks"][blockIdent])
        block.arrivTimestamp = t + self.nodes[destNodeIdent].data["offset"]
        self.nodes[destNodeIdent].updateBlockchain({blockIdent:block})
        return out
        
    def go(self):
        with open(self.filename,"w") as writeFile:
            writeFile.write("timestamp,eventId,eventData\n")
        
        while self.globalTime - self.startTime< self.runTime:
            u = -1.0*math.log(1.0-random.random())/self.birthRate
            eventType = ("nodeJoins", None)
            
            v = -1.0*math.log(1.0-random.random())/self.deathRate
            if v < u:
                eventType = ("nodeLeaves", None)
                u = v
            
            for nodeIdent in self.nodes:
                localBlockDiscoRate = self.nodes[nodeIdent].data["intensity"]/self.nodes[nodeIdent].data["blockchain"].diff
                v = -1.0*math.log(1.0-random.random())/localBlockDiscoRate
                if v < u:
                    eventType = ("blockDisco", nodeIdent)
                    u = v
                    
            for edgeIdent in self.edges:
                edge = self.edges[edgeIdent]
                pB = edge.data["pendingBlocks"]
                for pendingIdent in pB:
                    pendingData = pB[pendingIdent] # pendingDat = {"timeOfArrival":timeOfArrival, "destIdent":otherIdent, "block":blockToProp}
                    if pendingData["timeOfArrival"] - self.globalTime < u:
                        eventTime = ("blockArriv", (pendingData["destIdent"], edgeIdent, pendingData["block"]))
                        u = v
                        
            self.globalTime += u
            out = ""
            if eventTime[0] == "nodeJoins":
                out = self.eventNodeJoins(self.globalTime)
            elif eventTime[0] == "nodeLeaves":
                out = self.eventNodeLeaves(self.globalTime)
            elif eventTime[0] == "blockDisco":
                out = self.eventBlockDiscovery(eventTime[1], self.globalTime)
            elif eventTime[0] == "blockArriv":
                out = self.eventBlockArrival(eventTime[1], eventTime[2], eventTime[3], self.globalTime)
            else:
                print("WHAAAA")
                
            with open(self.filename, "a") as writeFile:
                writeFile.write(out + "\n")
                        
                        

                
            
        
            
