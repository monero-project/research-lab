import unittest
import math
import numpy as np
import copy
from collections import deque
import time

class Block(object):
    """ Fundamental object. Contains dict of pointers to parent blocks. """
    def __init__(self, idIn=None, parentList=None):
        if parentList is None:
            self.parents = {}
        else:
            self.parents = parentList
        self.id = copy.deepcopy(idIn)     # Hash of payload || header || extra2 and anything else i want to add later.
        self.data = None

class BlockDAG(object):
    """ Set of blocks (self.blocks), a distinguished genesis block, and a subset of leaf blocks (self.leaves)"""
    def __init__(self, genBlock=None):
        """ Creates vanilla BlockDAG with blank genesis block"""
        self.blocks = {}
        self.leaves = {}
        self.genesisBlock = None
        if genBlock is None:
            self.genesisBlock = Block()
        else:
            self.genesisBlock = copy.deepcopy(genBlock)
        self.blocks.update({copy.deepcopy(self.genesisBlock.id):self.genesisBlock})
        self.leaves.update({copy.deepcopy(self.genesisBlock.id):self.genesisBlock})
    def addBlock(self, blockIn):
        """ Add new leaf blockIn to BlockDAG, update leafset """
        self.blocks.update({blockIn.id:blockIn})
        self.leaves.update({blockIn.id:blockIn})
        q = deque()
        for parent in blockIn.parents:
            if parent in self.leaves:
                q.append(parent)
        while len(q)>0:
            parent = q.popleft()
            del self.leaves[parent]

class Spectre(object):
    """ Contains a BlockDAG, a dictionary of children, a dictionary
        of observed pasts, a dictionary of observed votes, and a
        dictionary keyToRep that takes a block ID as key and has as
        its value a representative block ID of some block with an
        identical past."""
    def __init__(self, dagIn=None):
        if dagIn is None:
            self.dag = BlockDAG()
        else:
            self.dag = dagIn
        self.children = {}
        self.seenPasts = {}
        self.seenVotes = {}
        self.keyToRep = {}
    def updateChildren(self):
        """ Update children dictionary: if child is a block with some
            parent, ensures that child is in self.children[parent]."""
        for child in self.dag.blocks:
            for parent in self.dag.blocks[child].parents:
                if parent not in self.children:
                    self.children.update({parent:[]})
                self.children[parent].append(child)
    def addBlock(self, blockIn):
        """ Takes block as input and includes it into the DAG and updates children."""
        self.dag.addBlock(blockIn)
        self.updateChildren()
    def getFutureIDs(self, blockID):
        """ Returns a dict of all block IDs of blocks in the future of blockID """
        result = {}
        q = deque()
        self.updateChildren()
        if blockID in self.children:
            for ch in self.children[blockID]:
                q.append(ch)
            while len(q)>0:
                ch = q.popleft()
                if ch not in result:
                    result.update({ch:ch})
        return result

    def getPast(self, blockID):
        """ Returns a sub-BlockDAG() with all the blocks from the past of blockID.
            This method is made marginally more efficient using keyToRep and only
            comping votes once for each given history. """
        result = None # This will be the result returned. If we get None something went wrong.
        if blockID in self.keyToRep: # In this case, we have computed the past before.
            result =  self.seenPasts[self.keyToRep[blockID]]
        else: # In this case, we must compute the past.
            q = deque()
            pastIDs = {} # This is just a dictionary of block IDs we will check against.
            for parent in self.dag.blocks[blockID].parents:
                q.append(parent) # Start a queue with all the parents of blockID.
            while len(q)>0: # Fill pastIDs with all past block IDs.
                nextID = q.popleft() # Take a block out of queue.
                if nextID not in pastIDs: # Record this blockID into dictionary pastIDs 
                    pastIDs.update({nextID:nextID})
                for parent in self.dag.blocks[nextID].parents:
                    q.append(parent) # For each parent of the current block, enqueue them.
            # now queue is empty
            result = BlockDAG(genBlock=self.dag.genesisBlock) # Create dummy new BlockDAG
            for child in self.children[self.dag.genesisBlock.id]:
                if child in pastIDs:
                    q.append(child) # Enqueue children of the genesis block that are in the past of blockID
            while len(q)>0:
                child = q.popleft() # Take a block out of queue.
                for ch in self.children[child]:
                    if ch in pastIDs: # Enqueue children of the block that are in the past of blockID
                        q.append(ch)
                if child not in result.blocks:
                    result.addBlock(blockIn=self.dag.blocks[child]) # Include current block into dummy BlockDAG
            self.seenPasts.update({blockID:copy.deepcopy(result)}) # Include dummy BlockDAG into seenPasts
            self.keyToRep.update({blockID:blockID}) # Include blockID in the equivalence class of blockID
            return result # Return dummy BlockDAG

    def stripLeaves(self, subdag):
        """ Takes as input a subdag and outputs a sub-subdag where all leaves from subdag have been deleted. """
        result = BlockDAG(subdag.genesisBlock)
        q = deque()
        q.append(subdag.genesisBlock.id)
        while len(q)>0:
            block = q.popleft()
            if block not in subdag.leaves:
                result.addBlock(subdag.blocks[block])
        return result  

    def getMajorityOfFuture(self, votingBlock, futureIDs, blockX, blockY, partial):
        s = 0
        result = None
        for fids in futureIDs:
            if (fids,blockX,blockY) in partial:
                s = s+1
            elif (fids, blockY, blockX) in partial:
                s = s-1
        if s > 0:
            result = (block,blockX,blockY)
        elif s < 0:
            result = (block,blockY,blockX)
        return result
    def getSum(self, result, subdag, partial):
        for blockX in subdag.blocks:
            for blockY in subdag.blocks:
                s = 0
                for votingBlock in subdag.blocks:
                    if (votingBlock, blockX, blockY) in partial:
                        s = s+1
                    elif (votingBlock, blockY, blockX) in partial:
                        s = s-1
                if s > 0:
                    result.update({(blockX,blockY):True})
                elif s < 0:
                    result.update({(blockY, blockX):True})
        return result
    def getVote(self, subdag=None):
        """ This algorithm takes a subdag as input and computes how that subdag votes on its own interior order.
            The output is a dictionary where all values are True and keys are of the form (blockX, blockY)
            signifying that the network has decided blockX < blockY.

            The total vote of the subdag on any pair of blocks (blockX, blockY) is defined as the majority of votes
            of the blocks in the subdag, i.e. the majority of votes of the form (votingBlock, blockX, blockY). Each 
            votingBlock votes using the following rules:
               (i)   blocks from the past of votingBlock should precede votingBlock and blocks not from the past of votingBlock
               (ii)  votingBlock should precede blocks not from the past of votingBlock
               (iii) votingBlock votes on pairs not from the past of votingBlock by majority of the future of votingBlock
               (iv)  votingBlock votes on pairs from the past of votingBlock by calling getVote on the past of votingBlock
        """
        result = {} # Dictionary initially empty.
        if subdag is None:
            subdag = copy.deepcopy(self.dag)
        for blockID in subdag.blocks:
            result.update({(blockID,blockID):True}) # All blocks vote reflexively: x <= x for each x
        if len(subdag.blocks) > 1:
            partial = {} # This dictionary will have all True values and keys of the form (votingBlock, blockX, blockY)
            for blockID in subdag.blocks:
                partial.update({(blockID,blockID,blockID):True}) # All votingBlocks vote reflexively for themselves.
            
            # We are first going to compute votes for leaves. Then, we will compute votes for the blocks
            # that would be leaves if all leaves of the current BlockDAG were to be deleted. We repeat
            # this as expected until we only have the genesis block remaining. We call the structure canopy.
            canopy = []
            nextdag = copy.deepcopy(subdag)
            while len(nextdag.blocks) > 1:
                canopy.append(nextdag.leaves)
                nextdag = self.stripLeaves(nextdag)
            
            for layer in canopy:
                for block in layer: # Compute votes from leaf-to-root as described above

                    # STEP 1: Get recursive vote, store in thisRecVote.
                    if block in self.keyToRep: 
                        # In this case, the past of block and its vote have been computed already
                        # and stored with key self.keyToRep[block] in self.seenPasts
                        # and self.seenVotes, respectively
                        thisPast = self.seenPasts[self.keyToRep[block]]
                        thisRecVote = self.seenVotes[self.keyToRep[block]]
                    else:
                        # In this case, we can't tell, maybe or maybe not: perhaps the past of 
                        # block has been computed, but the key self.keyToRep[block] has not 
                        # been determined yet. 
                        thisPast = self.getPast(block) # We first compute the past, see if it has been 
                        for key in self.seenPasts:     # computed before at any other key. If so, we
                            if self.seenPasts[key]==thisPast: # can pull up the recursive vote and
                                self.keyToRep.update({block:key}) # update the keyToRep to note the
                                thisRecVote = self.seenVotes[key] # alternative key.
                                break
                        else: # We enter this case if we did not find any past that matches thisPast.
                            self.keyToRep.update({block:block})  # In this case, keyToRep is identity
                            thisRecVote = self.getVote(thisPast) # And we recursively compute the vote
                            self.seenVotes.update({self.keyToRep[block]:thisRecVote}) # then we store 
                            self.seenPasts.update({self.keyToRep[block]:thisPast}) # the vote and the past.

                    # STEP 2: Get block IDs that have a vote on pairs from the past of block
                    futureIDs = self.getFutureIDs(block)

                    # STEP 3: For every pair of blocks, either both in the pair are in the past (see thisRecVote)
                    #         or one of the pair is in the past (inducing a natural order)
                    #         or both in the pair are not in the past (majority of votes from futureIDs)
                    for key in thisRecVote: # Extend thisRecVote into partial by taking each key of (blockX, blockY)
                        newVote = (block, copy.deepcopy(key[0]), copy.deepcopy(key[1])) # and inserting (votingBlock, blockX, blockY).
                        if newVote not in partial:
                            partial.update({newVote:True})
                    for blockX in subdag.blocks:
                        for blockY in subdag.blocks:
                            # Since we took thisRecVote into account, we can disregard the case: "both in past" 
                            if blockX in thisPast.blocks and blockY in thisPast.blocks:
                                pass
                            # If blockX is in the past of block and blockY is not, then block votes blockX < block < blockY
                            elif blockX in thisPast.blocks and blockY not in thisPast.blocks:
                                partial.update({(block,blockX,block):True,(block,blockX,blockY):True,(block,block,blockY):True})
                            # If blockY is in the past of block and blockX is not, then block votes blockY < block < blockX
                            elif blockX not in thisPast.blocks and blockY in thisPast.blocks:
                                partial.update({(block,blockY,block):True,(block,blockY,blockX):True,(block,block,blockX):True})
                            # If blockX and blockY not in the past, then....
                            elif blockX not in thisPast.blocks and blockY not in thisPast.blocks:
                                # Could be the that blockX=blockY=block.
                                if blockX == blockY and blockX == block:
                                    # partial.update({(block,block,block):True}) # Unnecessary, we already did this (line 150)
                                    pass
                                # Could be that blockY=block but blockX != block and blockX not in the past of block
                                # In this case, block votes that block < blockX.
                                elif blockX != block and blockY == block: 
                                    partial.update({(block,block,blockX):True})
                                # Could be that blockX=block but blockY != block and blockY not in the past of block.
                                # In this case, block votes that block < blockY
                                elif blockX == block and blockY != block:
                                    partial.update({(block, block, blockY):True})
                                # Last case: blockX != block != blockY, use majority of future blocks.
                                elif blockX != block and blockY != block:
                                    maj = self.getMajorityOfFuture(block, futureIDs, blockX, blockY, partial)
                                    if maj is not None:
                                        partial.update({maj:True})
                                else:
                                    print("DOOM AND GLOOM HOW DID YOU FIND YOURSELF HERE YOUNG CHILD?")
                for key in partial:
                    print("Key = ", key, ", \t, val = ", partial[key])
            result = self.getSum(result, subdag, partial)
        return result

class Test_Spectre(unittest.TestCase):
    def test_Spectre(self):
        # CREATE BLOCKCHAIN
        genBlock = Block(idIn="0")
        brock = BlockDAG(genBlock)
        shepard = Spectre(brock)
        
        newBlock = Block(idIn="1", parentList=shepard.dag.leaves)
        shepard.addBlock(copy.deepcopy(newBlock))
        vote = shepard.getVote()
        oldVote = copy.deepcopy(vote)
        self.assertTrue(("0","0") in vote)
        self.assertTrue(("0","1") in vote)
        self.assertTrue(("1","1") in vote)

        genBlock = Block(idIn="0")
        brock = BlockDAG(genBlock)
        shepard = Spectre(brock)
        block1 = Block(idIn="1", parentList={genBlock.id:genBlock})
        block2 = Block(idIn="2", parentList={genBlock.id:genBlock})
        block3 = Block(idIn="3", parentList={"1":block1, "2":block2})
        block4 = Block(idIn="4", parentList={"2":block2})
        shepard.addBlock(copy.deepcopy(block1))
        shepard.addBlock(copy.deepcopy(block2))
        shepard.addBlock(copy.deepcopy(block3))
        shepard.addBlock(copy.deepcopy(block4))
        vote = shepard.getVote()
        print(vote)
        self.assertTrue(("0","2") in vote)
        self.assertTrue(("2", "1") in vote)
        self.assertTrue(("1", "3") in vote)
        self.assertTrue(("3", "4") in vote)
        self.assertFalse(("4", "2") in vote)
        
        block3 = Block(idIn="3", parentList=shepard.dag.leaves)
        shepard.addBlock(block3)
        vote = shepard.getVote()
        for ov in oldVote:
            self.assertTrue(ov in vote)
        oldVote = copy.deepcopy(vote)
        for key in vote:
            print("key = ", key, " \t val = ", vote[key], "\n")
        self.assertTrue(("0","1") in vote)
        self.assertTrue(("1","2b") in vote)
        self.assertTrue(("2b","2a") in vote)
        self.assertTrue(("2a","3ab") in vote)
        self.assertTrue(("3ab","3b") in vote)
        self.assertFalse(("3b","1") in vote)
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_Spectre)
unittest.TextTestRunner(verbosity=1).run(suite)
           
