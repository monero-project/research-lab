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
        print("Initializing")
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
        print("Adding block")
        # Take a single block b and add to self.blocks, record family
        # relations, update leaf monitor, update root monitor if nec-
        # essary
        diffDict = {b.ident:b}
        self.blocks.update(diffDict)
        self.family.update({b.ident:{}})
        self.family[b.ident].update({"parents":b.parents, "children":{}})
        for parentIdent in b.parents:
            if parentIdent not in self.family:
                self.family.update({parentIdent:{}})
            if "parents" not in self.family[parentIdent]:
                self.family[parentIdent].update({"parents":{}})
            if "children" not in self.family[parentIdent]:
                self.family[parentIdent].update({"children":{}})
            self.family[parentIdent]["parents"].update(b.parents)
            self.family[parentIdent]["children"].update(diffDict)
            if parentIdent in self.leaves:
                del self.leaves[parentIdent]
        if len(b.parents)==0 and b.ident not in self.roots:
            self.roots.update(diffDict)
        self.leaves.update(diffDict)
        
    def inPast(self, x, y):
        print("Testing if in past")
        # Return true if y is an ancestor of x
        q = deque()
        for pid in self.blocks[x].parents:
            if pid==y:
                return True
                break
            q.append(pid)
        while(len(q)>0):
            nxtIdent = q.popleft()
            if len(self.blocks[nxtIdent].parents) > 0:
                for pid in self.blocks[nxtIdent].parents:
                    if pid==y:
                        return True
                        break
                    q.append(pid)
        return False
            
        
    def vote(self):
        print("Voting")
        # Compute partial spectre vote for top several layers of
        # the dag.
        (U, vids) = self.leafBackAntichain()
        self.votes = {}        
        
        q = deque()
        self.pendingVotes = {}
        for i in range(len(U)):
            for leafId in U[i]:
                if i > 0:
                    self.sumPendingVotes(leafId, vids)

                for x in U[i]:
                    if x != leafId:
                        q.append(x)
                while(len(q)>0):
                    x = q.popleft()
                    if (leafId, leafId, x) not in self.votes:
                        self.votes.update({(leafId, leafId, x):1})
                    else:
                        try:
                            assert self.votes[(leafId, leafId, x)]==1
                        except AssertionError:
                            print("Woops, we found (leafId, leafId, x) as a key in self.votes while running vote(), and it should be +1, but it isn't:\n\n", (leafId, leafId, x), self.votes[(leafId, leafId, x)], "\n\n")
                    if (leafId, x, leafId) not in self.votes:
                        self.votes.update({(leafId, x, leafId):-1})
                    else:
                        try:
                            assert self.votes[(leafId,x,leafId)]==-1
                        except AssertionError:
                            print("Woops, we found (leafId, x, leafId) as a key in self.votes while running vote(), and it should be +1, but it isn't:\n\n", (leafId, x, leafId), self.votes[(leafId, x, leafId)], "\n\n")
                    self.transmitVote(leafId, leafId, x)
                    for pid in self.blocks[x].parents:
                        if not self.inPast(leafId, pid) and pid in vids and pid != leafId: 
                            q.append(pid)
        print(self.votes)
                            
    def sumPendingVotes(self, blockId, vulnIds):
        print("Summing pending votes")
        # For a blockId, take all pending votes for vulnerable IDs (x,y)
        # if the net is positive vote 1, if the net is negative vote -1
        # otherwise vote 0.
        for x in vulnIds:
            for y in vulnIds:
                if (blockId, x, y) in self.pendingVotes:
                    if self.pendingVotes[(blockId, x, y)] > 0:
                        if (blockId, x, y) not in self.votes:
                            self.votes.update({(blockId, x, y):1})
                        else:
                            try:
                                assert self.votes[(blockId,x,y)]==1
                            except AssertionError:
                                print("Woops, we found (blockId, x, y) as a key in self.votes, and it should be +1, but it isn't:\n\n", (blockId, x, y), self.votes[(blockId, x,y)], "\n\n")
                        if (blockId, y, x) not in self.votes:
                            self.votes.update({(blockId, y, x):-1})
                        else:
                            try:
                                assert self.votes[(blockId,y,x)]==-1
                            except AssertionError:
                                print("Woops, we found (blockId, y, x) as a key in self.votes, and it should be -1, but it isn't:\n\n", (blockId, y, x), self.votes[(blockId, y,x)], "\n\n")
                        self.transmitVote(blockId, x, y)
                    elif self.pendingVotes[(blockId, x, y)] < 0:
                        if (blockId, x, y) not in self.votes:
                            self.votes.update({(blockId, x, y):-1})
                        else:
                            try:
                                assert self.votes[(blockId,x,y)]==-1
                            except AssertionError:
                                print("Woops, we found (blockId, x, y) as a key in self.votes, and it should be -1, but it isn't:\n\n", (blockId, x, y), self.votes[(blockId, x,y)], "\n\n")
                                
                        if (blockId, y, x) not in self.votes:
                            self.votes.update({(blockId, y, x):1})
                        else:
                            try:
                                assert self.votes[(blockId,y,x)]==1
                            except AssertionError:
                                print("Woops, we found (blockId, y, x) as a key in self.votes, and it should be +1, but it isn't:\n\n", (blockId, x, y), self.votes[(blockId, x,y)], "\n\n")
                        self.transmitVote(blockId, y, x)
                    else:
                        if (blockId, x, y) not in self.votes:
                            self.votes.update({(blockId, x, y):0})
                        else:
                            try:
                                assert self.votes[(blockId,x,y)]==0
                            except AssertionError:
                                print("Woops, we found (blockId, x, y) as a key in self.votes, and it should be 0, but it isn't:\n\n", (blockId, x, y), self.votes[(blockId, x,y)], "\n\n")
                        if (blockId, y, x) not in self.votes:
                            self.votes.update({(blockId, y, x):0})
                        else:
                            try:
                                assert self.votes[(blockId,y,x)]==0
                            except AssertionError:
                                print("Woops, we found (blockId, y, x) as a key in self.votes, and it should be 0, but it isn't:\n\n", (blockId, y, x), self.votes[(blockId, y,x)], "\n\n")                
                        
                    
                
        
    def transmitVote(self, v, x, y):
        print("Transmitting votes")
        q = deque()
        for pid in self.blocks[v].parents:
            q.append(pid)
        while(len(q)>0):
            print("Length of queue = ", len(q))
            nxtPid = q.popleft()
            if (nxtPid, x, y) not in self.pendingVotes:
                self.pendingVotes.update({(nxtPid,x,y):1})
                self.pendingVotes.update({(nxtPid,y,x):-1})
            else:
                self.pendingVotes[(nxtPid,x,y)] += 1
                self.pendingVotes[(nxtPid,y,x)] -= 1
            if len(self.blocks[nxtPid].parents) > 0:
                for pid in self.blocks[nxtPid].parents:
                    if pid != nxtPid:
                        q.append(pid)
                    
                        
            
    
    def leafBackAntichain(self):
        print("Computing antichain")
        temp = copy.deepcopy(self)
        decomposition = []
        vulnIdents = None
        decomposition.append(temp.leaves)
        vulnIdents = decomposition[-1]
        temp = temp.pruneLeaves()
        while(len(temp.blocks)>0 and len(decomposition) < self.antichainCutoff):
            decomposition.append(temp.leaves)
            for xid in decomposition[-1]:
                if xid not in vulnIdents:
                    vulnIdents.update({xid:decomposition[-1][xid]})
            temp = temp.pruneLeaves()
        return decomposition, vulnIdents
            
    def pruneLeaves(self):
        print("Pruning leaves")
        out = BlockHandler()
        q = deque()
        for rootIdent in self.roots:
            q.append(rootIdent)
        while(len(q)>0):
            thisIdent = q.popleft()
            if thisIdent not in self.leaves:
                out._addBlock(self.blocks[thisIdent])
                for chIdent in self.family[thisIdent]["children"]:
                    q.append(chIdent)
        return out

class Test_RoBlock(unittest.TestCase):
    def test_BlockHandler(self):
        R = BlockHandler()
        b = Block()
        b.data = "zirconium encrusted tweezers"
        b._recomputeIdent()
        R._addBlock(b)
        
        b = Block()
        b.data = "brontosaurus slippers cannot exist"
        b.addParents(R.leaves)
        R._addBlock(b)
        
        R.vote()
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_RoBlock)
unittest.TextTestRunner(verbosity=1).run(suite)
