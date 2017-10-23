from BlockDAG import *

class Spectre(object):
    """ """
    def __init__(self):
        self.dag = BlockDAG()
        self.childRelation = {}
    def setDAG(self, dagIn=None):
        if dagIn is None:
            self.dag = BlockDAG()
        else:
            self.dag = copy.deepcopy(dagIn)
        self.updateChildren() # self.childRelation is a dict: self.childRelation[key]={block with key in block.parents}
    def updateChildren(self):
        self.childRelation = {}
        q = deque()
        for blockID in self.dag.leaves:
            q.append(blockID)
        while len(q) > 0:
            blockID = q.popleft()
            for parent in self.dag.blocks[blockID].parents:
                q.append(parent)
                if parent not in self.childRelation:
                    self.childRelation.update({parent:[]})
                self.childRelation[parent].append(blockID)
    def vote(self, subdag=None):
        result = {}
        if subdag is None:
            result = self.vote(self.dag)
        elif len(subdag.blocks)>1:
            canopy = []
            nextdag = copy.deepcopy(subdag)
            while len(nextdag.blocks)>1:
                canopy.append(nextdag.leaves)
                nextdag = self.pruneLeaves(nextdag)
            partialVotes = {}
            for votingBlock in subdag.blocks:
                partialVotes.update({votingBlock:{}})
            for layer in canopy:
               for votingBlock in layer:
                   thisPast = self.getPast(votingBlock)
                   recursiveVote = self.vote(thisPast)
                   partialVotes[votingBlock] = copy.deepcopy(recursiveVote)
                   futureIDs = self.getFutureIDs(votingBlock)
                   for blockX in subdag.blocks:
                       for blockY in subdag.blocks:
                           if blockX in thisPast.blocks and blockY in thisPast.blocks:
                               pass
                           elif blockX in thisPast.blocks and blockY not in thisPast.blocks:
                               partialVotes[votingBlock].update({(blockX,votingBlock):True, (blockX, blockY):True, (votingBlock, blockY):True})
                           elif blockX not in thisPast.blocks and blockY in thisPast.blocks:
                               partialVotes[votingBlock].update({(blockY,votingBlock):True, (blockY,blockX):True, (votingBlock,blockX):True})
                           else:
                               partialVotes[votingBlock].update({(votingBlock,blockX):True, (votingBlock,blockY):True})
                               s=0
                               for fid in futureIDs:
                                  if fid in subdag.blocks:
                                      #print("partialvotes[fid]=",partialVotes[fid])
                                      if (blockX, blockY) in partialVotes[fid]:
                                          s = s+1
                                      elif (blockY, blockX) in partialVotes[fid]:
                                          s = s-1
                               if s > 0:
                                   partialVotes[votingBlock].update({(blockX,blockY):True})
                               elif s < 0:
                                   partialVotes[votingBlock].update({(blockY,blockX):True})
            for blockX in subdag.blocks:
                for blockY in subdag.blocks:
                    s = 0
                    for votingBlock in subdag.blocks:
                        if (blockX, blockY) in partialVotes[votingBlock]:
                            s=s+1
                        elif (blockY, blockX) in partialVotes[votingBlock]:
                            s=s-1
                    if s > 0:
                        result.update({(blockX,blockY):True})
                    elif s < 0:
                        result.update({(blockY,blockX):True})
        return result
    def pruneLeaves(self, subdag):
        newsubdag = BlockDAG()
        newsubdag.startDAG(subdag.genBlock.id, subdag.genBlock)
        q = deque()
        for child in self.childRelation[subdag.genBlock.id]:
            if child in subdag.blocks:
                q.append(child)
        while len(q) > 0:
            nextBlock = q.popleft()
            if nextBlock not in subdag.leaves:
                newsubdag.addLeaf(blockIn=subdag.blocks[nextBlock])
            if nextBlock in self.childRelation:
                if len(self.childRelation[nextBlock])>1:
                    for child in self.childRelation[nextBlock]:
                        if child in subdag.blocks:
                            q.append(child)
        return newsubdag
    def addBlock(self, blockIn=None):
        if blockIn == None:
            parents = copy.deepcopy(self.dag.leaves)
            blockID = str(len(self.dag)+1)
            blockIn = Block(blockID, parents)
        else:
            blockID = blockIn.id
        self.dag.addLeaf(blockIn)
        for parent in blockIn.parents:
            if parent not in self.childRelation:
                self.childRelation.update({parent:[]})
            self.childRelation[parent].append(blockID)

    def getPastIDs(self, block):
        thisPast = {}
        q = deque()
        self.updateChildren()
        for parent in self.dag.blocks[block].parents:
            q.append(parent)
        while len(q) > 0:
            nextPastBlockID = q.popleft()
            if nextPastBlockID not in thisPast:
                thisPast.update({nextPastBlockID:self.dag.blocks[nextPastBlockID]})
            for parent in self.dag.blocks[nextPastBlockID].parents:
                q.append(parent)
        return thisPast
    def getFutureIDs(self, block):
        thisFuture = {}
        q = deque()
        self.updateChildren()
        if block in self.childRelation:
            # If this is the case, then block has at least one child.
            for child in self.childRelation[block]:
                q.append(child)
            while len(q) > 0:
                nextFutureBlockID = q.popleft()
                if nextFutureBlockID not in thisFuture:
                    thisFuture.update({nextFutureBlockID:self.dag.blocks[nextFutureBlockID]})
                if nextFutureBlockID in self.childRelation:
                    if len(self.childRelation[nextFutureBlockID]) > 0:
                        for child in self.childRelation[nextFutureBlockID]:
                            q.append(child)
        else: # In this case, block has no children, so futureIDs should be empty.
            pass
        return thisFuture
    def getPast(self, block):
        pastIDs = self.getPastIDs(block)
        subdag = BlockDAG()
        subdag.startDAG(idIn = self.dag.genBlock.id, genBlockIn = self.dag.genBlock)
        q = deque()
        for child in self.childRelation[self.dag.genBlock.id]:
            if child in pastIDs:
                q.append(child)
        while len(q) > 0:
            nextBlock = q.popleft()
            if nextBlock in pastIDs:
                subdag.addLeaf(self.dag.blocks[nextBlock])
            for child in self.childRelation[nextBlock]:
                if child in pastIDs:
                    q.append(child)
        return subdag

class Test_Spectre(unittest.TestCase):
    def test_Spectre(self):
        shepard=Spectre()
        b0 = Block()
        b0.setID("0")
        shepard.dag.startDAG(idIn="0", genBlockIn=b0)
        self.assertTrue(len(shepard.dag.leaves)==1 and len(shepard.dag.blocks)==1)

        b1 = Block()
        b1.setParents(parentList={"0":b0})
        b1.setID("1")
        shepard.addBlock(b1)
        
        b2 = Block()
        b2.setParents(parentList={"0":b0})
        b2.setID("2")
        shepard.addBlock(b2)
        
        b3 = Block()
        b3.setParents(parentList={"1":b1, "2":b2})
        b3.setID("3") 
        shepard.addBlock(b3)

        b4 = Block()
        b4.setParents(parentList={"2":b2})
        b4.setID("4")
        shepard.addBlock(b4)

        self.assertTrue("0" in shepard.dag.blocks and "1" in shepard.dag.blocks and "2" in shepard.dag.blocks and "3" in shepard.dag.blocks and "4" in shepard.dag.blocks)
        self.assertTrue("3" in shepard.dag.leaves and "4" in shepard.dag.leaves)
        self.assertTrue(len(shepard.dag.blocks)==5 and len(shepard.dag.leaves)==2)
        self.assertTrue("0" in shepard.childRelation and "1" in shepard.childRelation and "2" in shepard.childRelation)
        self.assertFalse("3" in shepard.childRelation)
        self.assertFalse("4" in shepard.childRelation)
        self.assertTrue("1" in shepard.childRelation["0"] and "2" in shepard.childRelation["0"])
        self.assertTrue("3" in shepard.childRelation["1"])
        self.assertTrue("3" in shepard.childRelation["2"] and "4" in shepard.childRelation["2"])
        self.assertFalse("4" in shepard.childRelation["1"])
        self.assertFalse("0" in shepard.childRelation["1"])

        vote = shepard.vote()
        #print(vote)
        self.assertTrue(("0", "1") in vote and \
                        ("0", "2") in vote and \
                        ("0", "3") in vote and \
                        ("0", "4") in vote and \
                        ("2", "1") in vote and \
                        ("2", "3") in vote and \
                        ("2", "4") in vote and \
                        ("1", "3") in vote and \
                        ("1", "4") in vote and \
                        ("3", "4") in vote)


suite = unittest.TestLoader().loadTestsFromTestCase(Test_Spectre)
unittest.TextTestRunner(verbosity=1).run(suite)

           
