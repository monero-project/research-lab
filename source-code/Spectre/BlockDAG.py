from Block import *
 #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### ####
class BlockDAG(object):
    """ Collection of >=1 block. """
    def __init__(self, params=None):
        self.genesis = Block()
        self.genesis.id = "0"
        self.blocks = {self.genesis.id:self.genesis}
        self.leaves = {self.genesis.id:self.genesis}
 
        # Blocks from top-down antichain subsets covering >= 1/2 of blockDAG
        self.votBlocks = {self.genesis.id:self.genesis} 
        # Blocks from top-down antichain subsets "non-negl" likely to re-org
        self.ordBlocks = {self.genesis.id:self.genesis} 

        if params is not None:
            self.security = params
        else:
            self.security = 10
        self.vote = {}
        self.pending = {}
        for blockZ in self.votBlocks:
            for blockX in self.ordBlocks:
                for blockY in self.ordBlocks:
                    self.vote.update({(blockZ,blockX,blockY):0})
                    self.pending.update({(blockZ,blockX,blockY):0})

    def computeVote(self, dagIn):
        (canopy, fullCanopy) = self.pick(dagIn)
        for layer in fullCanopy:
            for blockZ in layer:
                if blockZ not in dagIn.votBlocks:
                    continue
                else:
                    for blockX in layer:
                        if blockX not in dagIn.ordBlocks:
                            continue
                        else:
                            for blockY in layer:
                                if blockY not in dagIn.ordBlocks:
                                    continue
                                else:
                                    if self.inPast(dagIn,blockY,blockZ) and self.inPast(dagIn,blockX,blockZ): 
                                        # then Z votes recursively
                                        if blockZ not in dagIn.seenPasts:
                                            dagIn.seenPasts.update({blockZ:dagIn.getPast(blockZ)})
                                            dagIn.seenVotes.update({blockZ:dagIn.vote(dagIn.seenPasts[blockZ])})    
                                        dagIn.vote.update({(blockZ,blockX,blockY):dagIn.seenVotes[blockZ][(blockX,blockY)], (blockZ,blockY,blockX):dagIn.seenVotes[blockZ][(blockY,blockX)], (blockZ,blockX,blockZ):1, (blockZ, blockZ, blockX):-1, (blockZ, blockY, blockZ):1, (blockZ, blockZ, blockY):-1})
                                    elif self.inPast(dagIn, blockY, blockZ) and not self.inPast(dagIn, blockX, blockZ):
                                        dagIn.vote.update({(blockZ,blockX,blockY):-1, (blockZ,blockY,blockX):1, (blockZ,blockX,blockZ):-1, (blockZ,blockZ,blockX):1, (blockZ,blockZ,blockY):-1, (blockZ,blockY,blockZ):1}) # Then Z votes Y < Z < X
                                    elif not self.inPast(dagIn, blockY, blockZ) and self.inPast(dagIn, blockX, blockZ):
                                        dagIn.vote.update({(blockZ,blockX,blockY):1, (blockZ,blockY,blockX):-1, (blockZ,blockX,blockZ):1, (blockZ,blockZ,blockX):-1, (blockZ,blockZ,blockY):1, (blockZ,blockY,blockZ):-1})  # Then Z votes X < Z < Y
                                    else:
                                        if dagIn.pending[(blockZ,blockX,blockY)] > 0:
                                            dagIn.vote.update({(blockZ,blockX,blockY):1, (blockZ,blockY,blockX):-1, (blockZ, blockX, blockZ):-1, (blockZ, blockZ, blockX):1, (blockZ, blockY, blockZ):-1, (blockZ, blockZ, blockY):1})
                                        elif dagIn.pending[(blockZ,blockX,blockY)] < 0:
                                            dagIn.vote.update({(blockZ,blockX,blockY):-1, (blockZ,blockY,blockX):1, (blockZ, blockX, blockZ):-1, (blockZ, blockZ, blockX):1, (blockZ, blockY, blockZ):-1, (blockZ, blockZ, blockY):1})
                                        else:
                                            dagIn.vote.update({(blockZ,blockX,blockY):0, (blockZ,blockY,blockX):0, (blockZ, blockX, blockZ):-1, (blockZ, blockZ, blockX):1, (blockZ, blockY, blockZ):-1, (blockZ, blockZ, blockY):1})
                                    q = deque()
                                    for p in dagIn.blocks[blockZ].parents:
                                        if p in dagIn.votBlocks:
                                            q.append(p)
                                    while(len(q)>0):
                                        nextBlock = q.popleft()
                                        if (nextBlock, blockX, blockY) not in dagIn.pending:
                                            dagIn.pending.update({(nextBlock, blockX,blockY):0})
                                        if (nextBlock, blockY, blockX) not in dagIn.pending:
                                            dagIn.pending.update({(nextBlock, blockY,blockX):0})
                                        if dagIn.vote[(blockZ,blockX,blockY)] > 0:
                                            dagIn.pending[(nextBlock,blockX,blockY)] += 1
                                            dagIn.pending[(nextBlock,blockY,blockX)] -= 1
                                        elif dagIn.vote[(blockZ,blockX,blockY)] < 0:
                                            dagIn.pending[(nextBlock,blockX,blockY)] -= 1
                                            dagIn.pending[(nextBlock,blockY,blockX)] += 1
                                        for p in dagIn.blocks[nextBlock].parents:
                                            if p in dagIn.votBlocks:
                                                q.append(p)  
        totalVote = {}
        for blockX in dagIn.ordBlocks:
            for blockY in dagIn.ordBlocks:
                if (blockX, blockY) not in totalVote:
                    totalVote.update({(blockX,blockY):0, (blockY,blockX):0})
                for blockZ in dagIn.votBlocks:
                    if dagIn.vote[(blockZ,blockX,blockY)] > 0:
                        totalVote[(blockX,blockY)] += 1
                    elif dagIn.vote[(blockZ,blockX,blockY)] < 0:
                        totalVote[(blockX,blockY)] -= 1
                if totalVote[(blockX,blockY)] > 0:
                    totalVote[(blockX,blockY)] = 1
                elif totalVote[(blockX,blockY)] < 0:
                    totalVote[(blockX,blockY)] = -1
        return totalVote
                                         
    def pick(self, dagIn):
        """ Pick voting blocks and orderable blocks """
        (canopy, fullCanopy) = self.antichain(dagIn)
        dagIn.votBlocks = {}
        dagIn.ordBlocks = {}
        idx = 0
        count = len(canopy[idx])
        for block in canopy[idx]:
            dagIn.votBlocks.update({block:dagIn.blocks[block]})
            dagIn.ordBlocks.update({blcok:dagIn.blocks[block]})
        numVoters = 1 - ((-len(dagIn.blocks))//2)
        while(count < numVoters):
            idx += 1
            count += len(canopy[idx])
            for block in canopy[idx]:
                dagIn.votBlocks.update({block:dagIn.blocks[block]})
                if idx < self.security:
                    dagIn.ordBlocks.update({block:dagIn.blocks[block]})
        return (canopy, fullCanopy)
            

    def makeBlock(self, idIn, parentsIn):
        assert idIn not in self.blocks
        newBlock = Block()
        newBlock.id = idIn
        newBlock.addParents(parentsIn)
        self.blocks.update({newBlock.id:newBlock})
        for parent in parentsIn:
            if parent in self.leaves:
                del self.leaves[parent]
            self.blocks[parent].addChild(newBlock)
        self.leaves.update({newBlock.id:newBlock})

    def pruneLeaves(self, dagIn):
        result = BlockDAG()
        result.genesis.id = dagIn.genesis.id
        q = deque()
        for child in dagIn.genesis.children:
            if child not in dagIn.leaves:
                q.append(child)
        while(len(q)>0):
            nextBlock = q.popleft()
            result.makeBlock(nextBlock, dagIn.blocks[nextBlock].parents)
            for child in dagIn.blocks[nextBlock].children:
                if child not in dagIn.leaves:
                    q.append(child)
        return result

    def antichain(self, dagIn):
        canopy = []
        fullCanopy = []
        nextDag = dagIn
        canopy.append(nextDag.leaves)
        fullCanopy.append(nextDag.leaves)
        while(len(nextDag.blocks)>1):
            nextDag = dagIn.pruneLeaves(dagIn)
            canopy.append(nextDag.leaves)
            fullCanopy.append(fullCanopy[-1])
            for leaf in nextDag.leaves:
                fullCanopy[-1].append(leaf)
            nextDag = self.pruneLeaves(dagIn)
        return (canopy, fullCanopy)

    def inPast(self, dagIn, y, x):
        """ self.inPast(dag, y,x) if and only if y is in the past of x in dag """
        found = False
        if y in dagIn.blocks[x].parents:
            found = True
        else:
            q = deque()
            for parent in dagIn.blocks[x].parents:
                q.append(parent)
            while(len(q)>0):
                nextBlock = q.popleft()
                if y in dagIn.blocks[nextBlock].parents:
                    found = True
                    break
                else:
                    for parent in dagIn.blocks[nextBlock].parents:
                        q.append(parent)
        return found

    def getPast(self, dagIn, block):
        subdag = BlockDAG()
        subdag.genesis = dagIn.genesis
        q = deque()
        for child in dagIn.genesis.children:
            if self.inPast(dagIn,child,block):
                q.append(child)
        while len(q) > 0:
            nextBlock = q.popleft()
            subdag.makeBlock(dagIn.blocks[nextBlock])
            for child in dagIn.blocks[nextBlock].children:
                if self.inPast(dagIn,child,block):
                    q.append(child)
        return subdag

 
class Test_BlockDAG(unittest.TestCase):
    def test_BlockDAG(self):
        dag = BlockDAG()
        self.assertTrue("0" in dag.blocks)
        self.assertTrue("0" in dag.leaves)
        self.assertTrue(len(dag.blocks)==1)
        self.assertTrue(len(dag.leaves)==1)
        b0 = dag.genesis

        dag.makeBlock("1",{"0":b0})
        b1 = dag.blocks["1"]
        self.assertTrue("1" in dag.blocks)
        self.assertTrue("1" in dag.leaves)
        self.assertTrue("0" not in dag.leaves)
        self.assertTrue(len(dag.blocks)==2)
        self.assertTrue(len(dag.leaves)==1)
        self.assertTrue("1" in b0.children)
        self.assertTrue("1" in dag.genesis.children)
        self.assertTrue("1" in dag.blocks[dag.genesis.id].children)
        
        dag.makeBlock("2", {"0":b0})
        b2 = dag.blocks["2"]

        dag.makeBlock("3", {"1":b1, "2":b2})
        b3 = dag.blocks["3"]
 
        dag.makeBlock("4", {"2":b2})
        b4 = dag.blocks["4"]

        print(dag.computeVote(dag))

        

suite = unittest.TestLoader().loadTestsFromTestCase(Test_BlockDAG)
unittest.TextTestRunner(verbosity=1).run(suite)
