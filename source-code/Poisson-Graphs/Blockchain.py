from Block import *
import math
from scipy.stats import *
from numpy import *
from copy import deepcopy

class Blockchain(object):
    ''' 
    Not a true blockchain, of course, but tracks block objects (timestamps) as above.
    Each node should be responsible for finding the chain with most cumulative work.
    Right now we assume Nakamoto consensus (konsensnakamoto).
    '''
    def __init__(self, params=[], verbosity=True):
        self.blocks = {}
        self.leaves = {}
        self.miningIdents = None
        self.mIdent = None
        self.verbose = verbosity
        self.diff = None
        self.targetRate = None
        self.mode = None
                
    def addBlock(self, blockToAdd):
        # In our model we assume difficulty scores of blocks are correct (otherwise they would
        # be rejected in the real life network, and we aren't trying to model spam attacks).
        assert blockToAdd.ident not in self.blocks
        if len(self.blocks)==0:
            # In this case, blockToAdd is a genesis block, so we set difficulty
            self.diff = deepcopy(blockToAdd.diff)
            
        self.blocks.update({blockToAdd.ident:blockToAdd})
        self.leaves.update({blockToAdd.ident:blockToAdd})
        if blockToAdd.parent in self.leaves:
            del self.leaves[blockToAdd.parent]
        self.whichLeaf()
        return self.computeDifficulty()
            
    def whichLeaf(self):
        # Determine which leaf shall be the parent leaf.
        # If the chain has forked *ever* this will not be the case.
        maxCumDiff = 0.0
        self.miningIdents = []
        for ident in self.leaves:
            tempCumDiff = 0.0
            thisBlockIdent = ident
            if self.blocks[thisBlockIdent].diff is not None:
                tempCumDiff += self.blocks[thisBlockIdent].diff
            while self.blocks[thisBlockIdent].parent is not None:
                thisBlockIdent = self.blocks[thisBlockIdent].parent
                if self.blocks[thisBLockIdent].diff is not None:
                    tempCumDiff += self.blocks[thisBlockIdent].diff
            if tempCumDiff > maxCumDiff:
                # If more than one leaf ties for maxCumDiff, each node in the 
                # network should pick one of these two arbitrarily. Since we 
                # are storing each blockchain in a hash table (unordered!), for 
                # each node in the network that observes a tie, each possible leaf
                # is equally likely to have been the first one found! So
                # we don't need to do anything for the node to select which chain
                # to work off of.
                self.miningIdents = [ident]
                maxCumDiff = tempCumDiff
            elif tempCumDiff == maxCumDiff:
                self.miningIdents.append(ident)
            #print("leaf ident = ", str(ident), ", and tempCumDiff = ", str(tempCumDiff), " and maxCumDiff = ", str(maxCumDiff))
        assert len(self.miningIdents) > 0
        self.mIdent = random.choice(self.miningIdents)
        
    
    # 1 block in 6*10^5 milliseconds=10min
    def computeDifficulty(self):
        result = None
        if self.mode=="Nakamoto":
            # Use MLE estimate of poisson process, compare to targetRate, update by multiplying by resulting ratio.
            #if self.verbose:
            #    print("Beginning update of difficulty with Nakamoto method")
            count = 2016
            #if self.verbose:
            #    print("Checking that blockchain is 2016*n blocks long and some mining identity has been set")
            if len(self.blocks) % 2016 == 0 and len(self.miningIdents) > 0:
                ident = self.mIdent
                topTime = deepcopy(self.blocks[ident].discoTimestamp)
                parent = self.blocks[ident].parent
                count = count - 1
                touched = False
                while count > 0 and parent is not None:
                    ident = deepcopy(parent)
                    parent = self.blocks[ident].parent
                    count = count - 1
                    touched = True
                if not touched:
                    mleDiscoRate = deepcopy(self.targetRate)
                else:
                    botTime = deepcopy(self.blocks[ident].discoTimestamp)
                
                    # Algebra is okay:
                    assert topTime != botTime
                    
                    # MLE estimate of arrivals per second:
                    mleDiscoRate = float(2015)/float(topTime - botTime)
                    
                    # Rates can't be negative, but this estimate could be (although it's highly unlikely given Bitcoin's standard choices
                    # of difficulty update rate, etc.
                    mleDiscoRate = abs(mleDiscoRate) 
                    
                    if self.verbose:
                        print("MLE disco rate = " + str(mleDiscoRate) + " and targetRate = " + str(self.targetRate))
                    # Rate must be positive... so the MLE for block arrival rate
                    # assuming a Poisson process _is not even well-defined_ as
                    # an estimate for block arrival rate assuming timestamps are
                    # inaccurately reported!
                    
                    # We use it nonetheless.
                
                if self.verbose:
                    print("MLE discovery rate = " + str(mleDiscoRate))
                    print("Difficulty before adjustment = " + str(self.diff))
                
                # Update difficulty multiplicatively
                self.diff = self.diff*mleDiscoRate/self.targetRate
                
                if self.verbose:
                    print("Difficulty after adjustment = ", str(self.diff))
                
        elif self.mode=="vanSaberhagen":
            # Similar to above, except use 1200 blocks, discard top 120 and bottom 120 after sorting.
            # 4 minute blocks in the original cryptonote, I believe... targetRate = 1.0/
            # 4 minutes/period, 60 seconds/minute ~ 240 seconds/period
            # assert targetRate==1.0/240.0
            count = 1200
            #print(self.diff)
            assert self.diff != 0.0
            if len(self.blocks) > 120 and len(self.miningIdents) > 0:
                ident = self.mIdent
                bl = []
                bl.append(deepcopy(self.blocks[ident].discoTimestamp))
                parent = self.blocks[ident].parent
                count = count - 1
                while count > 0 and parent is not None:
                    ident = deepcopy(parent)
                    bl.append(deepcopy(self.blocks[ident].discoTimestamp))
                    parent = self.blocks[ident].parent
                    count = count-1
                # sort    
                bl = sorted(bl)
                assert len(bl)<=1200
                
                #print("Sample size = " + str(len(bl)))
                # remove 10 and 90 %-iles
                numOutliers = math.ceil(float(len(bl))/float(10))
                assert numOutliers <= 120
                #print("Number of outliers = " + str(numOutliers))
                oldBL = deepcopy(bl)
                if numOutliers > 0:
                    bl = bl[numOutliers:-numOutliers]
                #if numOutliers == 120:
                #    print("\n\nSORTED TS LIST = " + str(oldBL) + "\nModified list = " + str(bl))
                    
                
                # get topTime and botTime
                #if self.verbose:
                #    print("bl[0] = " + str(bl[0]) + ",\tbl[-1] = " + str(bl[-1]))
                topTime = bl[-1]
                botTime = bl[0]
                result = [float(topTime - botTime)]
                #print(topTime - botTime)
                #if self.verbose:
                #    print("list of timestamps = " + str(bl))
                #    print("topTime = " + str(bl[-1]))
                #    print("botTime = " + str(bl[0]))
                
                # Assert algebra will work
                # 1200 - 2*120 = 1200 - 240 = 960
                assert 0 < len(bl) and len(bl) < 961
                assert topTime - botTime >= 0.0
                result.append(len(bl)-1)
                # Sort of the MLE: # blocks/difference in reported times
                # But not the MLE, since the reported times may not be 
                # the actual times, the "difference in reported times" != 
                # "ground truth difference in block discoery times" in general
                if len(bl)==0:
                    print("WOOP WOOP NO TIMESTAMPS WTF? We have " + str(len(self.blocks)) + " blocks available, and we are counting " + str(2*numOutliers) + " as outliers. bl = " + str(bl)) 
                naiveDiscoRate = float(len(bl)-1)/float(topTime - botTime)
                
                # How much should difficulty change?
                assert naiveDiscoRate != 0.0
                assert self.targetRate != 0.0 
                assert self.diff != 0.0
                self.diff = self.diff*naiveDiscoRate/self.targetRate
                
        elif self.mode=="MOM:expModGauss":
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
            #assert targetRate==1.0/120.0
            
            # Really a trash metric unless sample sizes are huge.
            count = 1200
            ident = self.mIdent
            bl = []
            bl.append(deepcopy(self.blocks[ident].discoTimestamp))
            parent = self.blocks[ident].parent
            count = count - 1
            while count > 0 and parent is not None:
                ident = deepcopy(parent)
                bl.append(deepcopy(self.blocks[ident].discoTimestamp))
                parent = self.blocks[ident].parent
                count = count-1
            if len(bl) > 120:
                sk   = abs(skew(bl))
                va   = var(bl)
                stdv = sqrt(va)
                lam  = (1.0/stdv)*(2.0/sk)**(1.0/3.0)
            else:
                lam = self.targetRate # we will not change difficulty unless we have at least 120 blocks of data (arbitrarily selected)
            self.diff = self.diff*(lam/self.targetRate)
        elif self.mode=="reciprocalOfMedian":
            # In this mode we use a bitcoin-style metric except instead of 1/average inter-arrival time
            # we use 1/median magnitude of inter-arrival time.
            # And updated each block like with monero instead of every 2016 blocks like bitcoin.
            # We assume a sample size of only 600 blocks for now
            count = 600
            interArrivals = []
            if len(self.blocks) < count:
                estDiscoRate = self.targetRate
            elif len(self.miningIdents) > 0:
                ident = self.mIdent
                parent = self.blocks[ident].parent
                if parent is not None:
                    dT = abs(self.blocks[ident].discoTimestamp - self.blocks[parent].discoTimestamp)
                    interArrivals.append(dT)
                count = count - 1
                touched = False
                while count > 0 and parent is not None:
                    ident = deepcopy(parent)
                    parent = self.blocks[ident].parent
                    if parent is not None:
                        dT = abs(self.blocks[ident].discoTimestamp - self.blocks[parent].discoTimestamp)
                        interArrivals.append(dT)
                    count = count - 1
                    touched = True
                if not touched:
                    estDiscoRate = self.targetRate
                else:
                    estDiscoRate = 1.0/median(interArrivals)
                    if self.verbose:
                        print("Est disco rate = " + str(estDiscoRate) + " and targetRate = " + str(self.targetRate))
                    
                
                if self.verbose:
                    print("MLE discovery rate = " + str(estDiscoRate))
                    print("Difficulty before adjustment = " + str(self.diff))
                
                # Update difficulty multiplicatively
                self.diff = self.diff*estDiscoRate/self.targetRate
                
                if self.verbose:
                    print("Difficulty after adjustment = ", str(self.diff))
        else:
            print("Error, invalid difficulty mode entered.")
        return result
           
class Test_Blockchain(unittest.TestCase):
    def test_addBlock(self):
        bill = Blockchain([], verbosity=True)
        bill.mode="Nakamoto"
        tr = 1.0/100.0
        bill.targetRate = tr
        
        name = newIdent(0)
        t = time.time()
        s = t+random.random()
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
        genesis = Block(params)
        
        self.assertEqual(genesis.ident,name)
        self.assertEqual(genesis.discoTimestamp,t)
        self.assertEqual(genesis.arrivTimestamp,s)
        self.assertTrue(genesis.parent is None)
        self.assertEqual(genesis.diff,diff)
        
        bill.addBlock(genesis)
        
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertTrue(genesis.ident in bill.leaves)
        self.assertEqual(len(bill.miningIdents),1)
        self.assertEqual(genesis.ident, bill.miningIdents[0])
        self.assertEqual(len(bill.blocks),1)
        
        name = newIdent(1)
        t = time.time()
        s = t+random.random()
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":genesis.ident, "diff":diff}
        blockA = Block(params)
        bill.addBlock(blockA)
        
        self.assertTrue(blockA.ident in bill.blocks)
        self.assertTrue(blockA.ident in bill.leaves)
        self.assertTrue(genesis.ident not in bill.leaves)
        self.assertEqual(len(bill.miningIdents),1)
        self.assertEqual(blockA.ident, bill.miningIdents[0])
        self.assertEqual(len(bill.blocks),2)
        
        
        
        
        
        bill = Blockchain([], verbosity=True)
        mode="vanSaberhagen"
        tr = 1.0/100.0
        bill.targetRate = tr
        
        name = newIdent(0)
        t = time.time()
        s = t+random.random()
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
        genesis = Block(params)
        
        self.assertEqual(genesis.ident,name)
        self.assertEqual(genesis.discoTimestamp,t)
        self.assertEqual(genesis.arrivTimestamp,s)
        self.assertTrue(genesis.parent is None)
        self.assertEqual(genesis.diff,diff)
        
        bill.addBlock(genesis, mode, tr)
        
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertTrue(genesis.ident in bill.leaves)
        self.assertEqual(len(bill.miningIdents),1)
        self.assertEqual(genesis.ident, bill.miningIdents[0])
        self.assertEqual(len(bill.blocks),1)
        
        name = newIdent(1)
        t = time.time()
        s = t+random.random()
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":genesis.ident, "diff":diff}
        blockA = Block(params)
        bill.addBlock(blockA, mode, tr)
        
        self.assertTrue(blockA.ident in bill.blocks)
        self.assertTrue(blockA.ident in bill.leaves)
        self.assertTrue(genesis.ident not in bill.leaves)
        self.assertEqual(len(bill.miningIdents),1)
        self.assertEqual(blockA.ident, bill.miningIdents[0])
        self.assertEqual(len(bill.blocks),2)
        
        
        
        
        
        bill = Blockchain([], verbosity=True)
        mode="MOM:expModGauss"
        tr = 1.0/100.0
        bill.targetRate = tr
        
        name = newIdent(0)
        t = time.time()
        s = t+random.random()
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
        genesis = Block(params)
        
        self.assertEqual(genesis.ident,name)
        self.assertEqual(genesis.discoTimestamp,t)
        self.assertEqual(genesis.arrivTimestamp,s)
        self.assertTrue(genesis.parent is None)
        self.assertEqual(genesis.diff,diff)
        
        bill.addBlock(genesis, mode, tr)
        
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertTrue(genesis.ident in bill.leaves)
        self.assertEqual(len(bill.miningIdents),1)
        self.assertEqual(genesis.ident, bill.miningIdents[0])
        self.assertEqual(len(bill.blocks),1)
        
        name = newIdent(1)
        t = time.time()
        s = t+random.random()
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":genesis.ident, "diff":diff}
        blockA = Block(params)
        bill.addBlock(blockA, mode, tr)
        
        self.assertTrue(blockA.ident in bill.blocks)
        self.assertTrue(blockA.ident in bill.leaves)
        self.assertTrue(genesis.ident not in bill.leaves)
        self.assertEqual(len(bill.miningIdents),1)
        self.assertEqual(blockA.ident, bill.miningIdents[0])
        self.assertEqual(len(bill.blocks),2)
        
        
    def test_bc(self):
        bill = Blockchain([], verbosity=True)
        mode="Nakamoto"
        tr = 1.0/100.0
        bill.targetRate = tr
        
        name = newIdent(0)
        t = time.time()
        s = t+1
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
        genesis = Block(params)
        
        self.assertEqual(genesis.ident,name)
        self.assertEqual(genesis.discoTimestamp,t)
        self.assertEqual(genesis.arrivTimestamp,t+1)
        self.assertTrue(genesis.parent is None)
        self.assertEqual(genesis.diff,diff)
        
        bill.addBlock(genesis, mode, tr)
        
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertTrue(genesis.ident in bill.leaves)
        self.assertEqual(len(bill.miningIdents),1)
        self.assertEqual(genesis.ident, bill.miningIdents[0])
        
        name = newIdent(1)
        t = time.time()
        s = t+1
        diff = 2.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":genesis.ident, "diff":diff}
        blockA = Block(params)
        bill.addBlock(blockA, mode, tr)
        
        #bill.whichLeaf()
        
        self.assertTrue(blockA.ident in bill.blocks)
        self.assertTrue(blockA.ident in bill.leaves)
        self.assertFalse(genesis.ident in bill.leaves)
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertEqual(len(bill.miningIdents),1)
        self.assertEqual(blockA.ident, bill.miningIdents[0])
        
        name = newIdent(1)
        t = time.time()
        s = t+1
        diff = 2.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":genesis.ident, "diff":diff}
        blockB = Block(params)
        bill.addBlock(blockB, mode, tr)
        
        self.assertTrue(blockB.ident in bill.blocks)
        self.assertTrue(blockB.ident in bill.leaves)
        self.assertEqual(bill.blocks[blockB.ident].parent, genesis.ident)
        
        self.assertTrue(blockA.ident in bill.blocks)
        self.assertTrue(blockA.ident in bill.leaves)
        self.assertEqual(bill.blocks[blockA.ident].parent, genesis.ident)
        
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertFalse(genesis.ident in bill.leaves)
        self.assertTrue(bill.blocks[genesis.ident].parent is None)
        
        #bill.whichLeaf()
        #print(bill.miningIdents)
        
        self.assertEqual(type(bill.miningIdents), type([]))
        self.assertTrue(len(bill.miningIdents), 2)
        
        name = newIdent(2)
        t = time.time()
        diff = 3.14159
        params = {"ident":name, "disco":t, "arriv":s, "parent":blockB.ident, "diff":diff}
        blockC = Block(params)
        bill.addBlock(blockC, mode, tr)
        
        self.assertTrue(blockC.ident in bill.blocks)
        self.assertTrue(blockC.ident in bill.leaves)
        
        self.assertTrue(blockB.ident in bill.blocks)
        self.assertFalse(blockB.ident in bill.leaves)
        
        self.assertTrue(blockA.ident in bill.blocks)
        self.assertTrue(blockA.ident in bill.leaves)
        
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertFalse(genesis.ident in bill.leaves)
        
        #bill.whichLeaf()
        
        #for blockIdent in bill.blocks:
        #    ident = bill.blocks[blockIdent].ident
        #    disco = bill.blocks[blockIdent].discoTimestamp
        #    arriv = bill.blocks[blockIdent].arrivTimestamp
        #    parent = bill.blocks[blockIdent].parent
        #    diff = bill.blocks[blockIdent].diff
        #    print(str(ident) + ", " + str(disco) + ", " + str(arriv) + ", " + str(parent) + ", " + str(diff) + ", " + str() + "\n")
        #print(bill.miningIdents)
        self.assertEqual(len(bill.miningIdents), 1)
        self.assertEqual(bill.miningIdents[0], blockC.ident)
    
    def test_median(self):
        # TODO: everything.
        mode = "reciprocalOfMedian"
        tr = 1.0 # one block per millisecond why not
        deltaT = 1.0 # let's just make this easy
        bill = Blockchain([], verbosity=True)
        bill.targetRate = tr
        
        with open("outputM.txt", "w") as writeFile:
            # We will send (t, a, diff) to writeFile.
            writeFile.write("time,rateConstant,difficulty\n")
            name = newIdent(0)
            t = 0.0
            s = 0.0
            diff = 1.0
            params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
            genesis = Block(params)
            
            self.assertEqual(genesis.ident,name)
            self.assertEqual(genesis.discoTimestamp,t)
            self.assertEqual(genesis.arrivTimestamp,s)
            self.assertTrue(genesis.parent is None)
            self.assertEqual(genesis.diff,diff)
            
            bill.addBlock(genesis, mode, tr)
            a = 1.0
            b = 1.0/a
            
            writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "\n")
            
            self.assertTrue(genesis.ident in bill.blocks)
            self.assertTrue(genesis.ident in bill.leaves)
            self.assertEqual(len(bill.miningIdents),1)
            self.assertEqual(genesis.ident, bill.miningIdents[0])
            
            parent = genesis.ident
            oldDiff = bill.diff
            
            while len(bill.blocks)<601:
                newName = newIdent(len(bill.blocks))
                t += deltaT*a
                s += deltaT*a
                self.assertEqual(bill.diff, oldDiff)
                diff = bill.diff
                params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
                newBlock = Block(params)
                bill.addBlock(newBlock, mode, tr)
                
                writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "\n")   
                parent = newName
                oldDiff = bill.diff
            
            a = 1.01 # slightly slower blocks, median won't change until half the data is corrupted!
            b = 1.0/a
            while len(bill.blocks)<899:
                newName = newIdent(len(bill.blocks))
                t += deltaT*a
                s += deltaT*a
                self.assertEqual(bill.diff, oldDiff)
                diff = bill.diff
                params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
                newBlock = Block(params)
                bill.addBlock(newBlock, mode, tr)
                self.assertEqual(bill.diff, oldDiff)
                writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "\n")   
                parent = newName
                oldDiff = bill.diff
                
            # One more block and our median inter-arrival time is deltaT*(1.0+a)/2.0 
            # and so estRate = 1/median = (2.0/(1.0+a))/deltaT, whereas before it was just
            # 1/deltaT. So estRate/targetRate = 2.0/(1.0+a)
            newName = newIdent(len(bill.blocks))
            t += deltaT*a
            s += deltaT*a
            self.assertEqual(bill.diff, oldDiff)
            diff = bill.diff
            params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
            newBlock = Block(params)
            bill.addBlock(newBlock, mode, tr)
            err = bill.diff - oldDiff*2.0/(1.0+a)
            self.assertTrue(err*err < 10**-15)
            writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "\n")   
            parent = newName
            oldDiff = bill.diff
                
            # One more block and our median inter-arrival time is deltaT*a 
            # and so estRate = 1/median = (1.0/a)/deltaT, whereas before it was just
            # 1/deltaT. So estRate/targetRate = 1.0/a = b
            newName = newIdent(len(bill.blocks))
            t += deltaT*a
            s += deltaT*a
            self.assertEqual(bill.diff, oldDiff)
            diff = bill.diff
            params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
            newBlock = Block(params)
            bill.addBlock(newBlock, mode, tr)
            err = bill.diff - oldDiff*b
            self.assertTrue(err*err < 10**-15)
            writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "\n")   
            parent = newName
            oldDiff = bill.diff
            
            # Note that until the median changes again, this estimated block arrival rate
            # does not change. This may be true even if a lot of new data has come in. 
            # It is possible that the same pair of blocks remain the median inter-arrival
            # magnitude for the entire time both blocks are in the sample size.
            # During this period of time, difficulty will update multiplicatively, so
            # will either exponentially grow or shrink.
            # In other words, this model can be looked at as: exponential change over
            # time with a rate proportional to the deviation between the median and
            # the target inter-arrival rates.
            
            
                
              
    
    def test_mine(self):
        # TODO: everything.
        mode = "MOM:expModGauss"
        tr = 1.0/120000.0 # one block per two minutes
        deltaT = 120000.0
        bill = Blockchain([], verbosity=True)
        bill.targetRate = tr
        
        with open("outputM.txt", "w") as writeFile:
            # We will send (t, a, diff, ratio, awayFromOne) to writeFile.
            writeFile.write("time,rateConstant,difficulty\n")
            name = newIdent(0)
            t = 0.0
            s = 0.0
            diff = 1.0
            params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
            genesis = Block(params)
            
            self.assertEqual(genesis.ident,name)
            self.assertEqual(genesis.discoTimestamp,t)
            self.assertEqual(genesis.arrivTimestamp,s)
            self.assertTrue(genesis.parent is None)
            self.assertEqual(genesis.diff,diff)
            
            bill.addBlock(genesis, mode, tr)
            a = 1.0
            b = 1.0/a
            
            writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "\n")
            
            self.assertTrue(genesis.ident in bill.blocks)
            self.assertTrue(genesis.ident in bill.leaves)
            self.assertEqual(len(bill.miningIdents),1)
            self.assertEqual(genesis.ident, bill.miningIdents[0])
            
            parent = genesis.ident
            oldDiff = bill.diff
            
            while len(bill.blocks)<120:
                # Our metric divides by skewness. In reality, this is zero with
                # probability zero. But for our tests, it's assured. So we
                # will perturb each arrival by a small, up-to-half-percent
                # variation to ensure a nonzero skewness without altering things
                # too much.
                newName = newIdent(len(bill.blocks))
                t += deltaT*a*(1.0 + (2.0*random.random() - 1.0)/100.0)
                s += deltaT*a*(1.0 + (2.0*random.random() - 1.0)/100.0)
                self.assertEqual(bill.diff, oldDiff)
                diff = bill.diff
                params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
                newBlock = Block(params)
                bill.addBlock(newBlock, mode, tr)
                
                writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "\n")   
                parent = newName
                oldDiff = bill.diff
                
            # Just one more block and difficulty should be computed for the first time.
            print("Just one more block and difficulty should be computed for the first time.")
            self.assertEqual(bill.diff, oldDiff)
            newName = newIdent(len(bill.blocks))
            t += deltaT*a*(1.0 + (2.0*random.random() - 1.0)/100.0)
            s += deltaT*a*(1.0 + (2.0*random.random() - 1.0)/100.0)
            diff = bill.diff
            params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
            newBlock = Block(params)
            bill.addBlock(newBlock, mode, tr) 
            writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "\n")
            parent = newName
            #self.assertEqual(bill.diff, oldDiff)
              
            oldDiff = bill.diff
            
            # what if we add a bunch of blocks this way?
            # In the case of a static hash rate, I suppose we hope to not
            # vary too far from a multiplicative factor of 1.0, or rather
            # a constant difficulty.
            
            while len(bill.blocks)<200:
                # Our metric divides by skewness. In reality, this is zero with
                # probability zero. But for our tests, it's assured. So we
                # will perturb each arrival by a small, up-to-half-percent
                # variation to ensure a nonzero skewness without altering things
                # too much.
                newName = newIdent(len(bill.blocks))
                t += deltaT*a*(1.0 + (2.0*random.random() - 1.0)/100.0)
                s += deltaT*a*(1.0 + (2.0*random.random() - 1.0)/100.0)
                self.assertEqual(bill.diff, oldDiff)
                diff = bill.diff
                params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
                newBlock = Block(params)
                bill.addBlock(newBlock, mode, tr)
                
                writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "\n")   
                parent = newName
                oldDiff = bill.diff
              
       
    
    def test_vs(self):
        # TODO: Still must test that outliers are being removed "appropriately" according to specifications
        # TODO: Test that scrambled lists of timestamps produce the same difficulty estimate.
        # TODO: Show that in the case of homogeneous poisson processes, unusual estimates are a little
        # more common than in the Nakamoto difficulty (which must be the case because Nakamoto uses
        # the UMVUE).
        mode = "vanSaberhagen"
        tr = 1.0/60000.0 # one block per minute
        deltaT = 60000.0
        bill = Blockchain([], verbosity=True)
        bill.targetRate = tr
        
        with open("output.txt", "w") as writeFile:
            # We will send (t, a, diff, ratio, awayFromOne) to writeFile.
            writeFile.write("time,rateConstant,difficulty,ratio\n")
            name = newIdent(0)
            t = 0.0
            s = 0.0
            diff = 1.0
            params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
            genesis = Block(params)
            
            self.assertEqual(genesis.ident,name)
            self.assertEqual(genesis.discoTimestamp,t)
            self.assertEqual(genesis.arrivTimestamp,s)
            self.assertTrue(genesis.parent is None)
            self.assertEqual(genesis.diff,diff)
            
            bill.addBlock(genesis, mode, tr)
            writeFile.write(str(t) + ",1.0," + str(bill.diff) + ",1.0\n")
            
            self.assertTrue(genesis.ident in bill.blocks)
            self.assertTrue(genesis.ident in bill.leaves)
            self.assertEqual(len(bill.miningIdents),1)
            self.assertEqual(genesis.ident, bill.miningIdents[0])
            self.assertEqual(bill.diff, 1.0)
            
            parent = genesis.ident
            oldDiff = bill.diff
            a = 1.0
            b = 1.0/a
            
            while len(bill.blocks)<120:
                newName = newIdent(len(bill.blocks))
                t += deltaT*a
                s += deltaT*a
                self.assertEqual(bill.diff, oldDiff)
                diff = bill.diff
                params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
                newBlock = Block(params)
                bill.addBlock(newBlock, mode, tr)
                
                writeFile.write(str(t) + ",1.0," + str(bill.diff) + ",1.0\n")   
                parent = newName
                oldDiff = bill.diff
                
            # Just one more block and difficulty should be computed for the first time.
            print("Just one more block and difficulty should be computed for the first time.")
            self.assertEqual(bill.diff, oldDiff)
            newName = newIdent(len(bill.blocks))
            t += deltaT*a
            s += deltaT*a
            diff = bill.diff
            params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
            newBlock = Block(params)
            bill.addBlock(newBlock, mode, tr) 
            writeFile.write(str(t) + ",1.0," + str(bill.diff) + ",1.0\n")
            parent = newName
            self.assertEqual(bill.diff, oldDiff)
              
            oldDiff = bill.diff
            
            print("Let's add more blocks at the same rate.")
            a = 1.0
            b = 1.0/a
            
            while len(bill.blocks)<1200:
                newName = newIdent(len(bill.blocks))
                t += deltaT*a
                s += deltaT*a
                diff = bill.diff
                params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
                newBlock = Block(params)
                
                bill.addBlock(newBlock, mode, tr)
                writeFile.write(str(t) + ",1.0," + str(bill.diff) + ",1.0\n")
                parent = newName
                self.assertEqual(bill.diff, oldDiff)
                oldDiff = bill.diff
            
            print("Let's add more blocks at a slower rate.")
            a = 1.1
            b = 1.0/a
            
            # If blocks arrive slightly further apart, difficulty should drop.
            # However, since vanSaberhagen discards top 10% and bottom 10% of
            # timestamps, it will take 120 blocks for this change to register
            # in difficulty.
            print("If blocks arrive slightly further apart, difficulty should drop. However, since vanSaberhagen discards top 10% and bottom 10% of timestamps, it will take 120 blocks for this change to register in difficulty.")
            while len(bill.blocks)<1320:
                newName = newIdent(len(bill.blocks))
                t += deltaT*a
                s += deltaT*a
                diff = bill.diff
                params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
                newBlock = Block(params)
                
                bill.addBlock(newBlock, mode, tr)
                writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "," + str(bill.diff/oldDiff) + "\n")
                parent = newName
                self.assertEqual(bill.diff, oldDiff)
                oldDiff = bill.diff
                
            print("One more block and difficulty should register a change.")
            self.assertEqual(bill.diff, oldDiff)
            newName = newIdent(len(bill.blocks))
            t += deltaT*a
            s += deltaT*a
            diff = bill.diff
            params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
            newBlock = Block(params)
            bill.addBlock(newBlock, mode, tr) 
            writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "," + str(bill.diff/oldDiff) + "\n")
            parent = newName
            self.assertTrue(bill.diff < oldDiff)
            oldDiff = bill.diff
            
            # Let's add another fifty blocks at this same rate and verify that difficulty continually
            # drops.
            print("Let's add another fifty blocks at this same rate and verify that difficulty continually drops.")
            a = 1.1
            b = 1.0/a
            
            while len(bill.blocks)<1370:
                newName = newIdent(len(bill.blocks))
                t += deltaT*a
                s += deltaT*a
                diff = bill.diff
                params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
                newBlock = Block(params)
                
                bill.addBlock(newBlock, mode, tr)
                writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "," + str(bill.diff/oldDiff) + "\n")
                parent = newName
                self.assertTrue(bill.diff < oldDiff)
                oldDiff = bill.diff
                
            # Now we go back to the target rate. We have 170 slow blocks in the queue and 50 in the sample size. Difficulty will continue to drop for another 120 blocks...
            print("Now we go back to the target rate. We have 170 slow blocks in the queue and 50 in the sample size. Difficulty will continue to drop for another 120 blocks...")
            a = 1.0
            b = 1.0/a
            
            while len(bill.blocks)<1490:
                newName = newIdent(len(bill.blocks))
                t += deltaT*a
                s += deltaT*a
                diff = bill.diff
                params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
                newBlock = Block(params)
                
                bill.addBlock(newBlock, mode, tr)
                writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "," + str(bill.diff/oldDiff) + "\n")
                parent = newName
                self.assertTrue(bill.diff < oldDiff)
                oldRatio = bill.diff/oldDiff
                oldDiff = bill.diff
                #print(str(result) + ", " + str(bill.diff) + ", " + str(oldDiff))
                
            # Now all 170 slow blocks are not only in the queue but in our sample. The *multiplicative factor* between timesteps should be identical for the next 790 blocks.. leading to AN EXPONENTIAL DECAY OF DIFFICULTY.
            print("Now all 170 slow blocks are not only in the queue but in our sample. The *multiplicative factor* between timesteps should be identical for the next 790 blocks.. leading to AN EXPONENTIAL DECAY OF DIFFICULTY.")
            a = 1.0
            b = 1.0/a
            while len(bill.blocks)<2279:
                newName = newIdent(len(bill.blocks))
                t += deltaT
                s += deltaT
                diff = bill.diff
                params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
                newBlock = Block(params)
                
                bill.addBlock(newBlock, mode, tr)
                writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "," + str(bill.diff/oldDiff) + "\n")
                ratio = bill.diff/oldDiff
                parent = newName
                err = ratio - oldRatio
                #print("Difference between last ratio and next ratio:" + str(err))
                self.assertTrue(err*err < 10**-15)
                oldDiff = bill.diff
                oldRatio = ratio
                
            print("Now adding a single new block will cause our 170 slow blocks to start dropping out of our sample, so the ratio should start returning to 1.0.")
            oldAwayFromOne = abs(oldRatio - 1.0) # Ratio should be returning to 1.0 so this difference should go to zero
            oldAwayFromOne = oldAwayFromOne*oldAwayFromOne
                
            # For the next 170 blocks as our perturbed blocks drop out of our sample, our 
            # estimated block arrival rate will return to "normal" so the multiplicative
            # difference in difficulty should return to 1.0.
            print("For the next 170 blocks as our perturbed blocks drop out of our sample, ourestimated block arrival rate will return to normal so the multiplicative difference in difficulty should return to 1.0.")
            a = 1.0
            b = 1.0/a
            while len(bill.blocks)<2449:
                newName = newIdent(len(bill.blocks))
                t += deltaT*a
                s += deltaT*a
                diff = bill.diff
                params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
                newBlock = Block(params)
                
                bill.addBlock(newBlock, mode, tr)
                writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "," + str(bill.diff/oldDiff) + "\n")
                ratio = bill.diff/oldDiff
                #print("New ratio = " + str(ratio) + " and oldRatio = " + str(oldRatio))
                self.assertTrue(ratio > oldRatio)
                awayFromOne = abs(ratio - 1.0) # Ratio should be returning to 1.0 so this difference should go to zero
                awayFromOne = awayFromOne*awayFromOne
                self.assertTrue(awayFromOne < oldAwayFromOne) # This return will be monotonic in our manufactured example.
                parent = newName
                oldDiff = bill.diff
                oldRatio = ratio
                oldAwayFromOne = awayFromOne
            
            
            # Now difficulty should remain frozen for as long as we like.
            
            a = 1.0
            b = 1.0/a
            while len(bill.blocks)<2500:
                newName = newIdent(len(bill.blocks))
                t += deltaT*a
                s += deltaT*a
                diff = bill.diff
                params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
                newBlock = Block(params)
                
                bill.addBlock(newBlock, mode, tr)
                writeFile.write(str(t) + "," + str(a) + "," + str(bill.diff) + "," + str(bill.diff/oldDiff) + "\n")
                parent = newName
                self.assertEqual(bill.diff, oldDiff)
                oldDiff = bill.diff
                
        
         
     
    def test_nak(self):
        # Since Nakamoto difficulty is derived from the MLE of the block arrival rate,
        # we already know how it "should" behave in a poisson process, etc.
        # TODO: Generate N samples of MLEs of Poisson rates compared to known homog. 
        # poisson rate, show that the resulting code does not result in unusual measurements
        # more often than expected.
        mode = "Nakamoto"
        tr = 1.0/600000.0
        deltaT = 600000.0
        bill = Blockchain([], verbosity=True)
        bill.targetRate = tr
        # Bitcoin updating at 1 block per 10 minutes
        
        name = newIdent(0)
        t = 0.0
        s = 0.0
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
        genesis = Block(params)
        
        self.assertEqual(genesis.ident,name)
        self.assertEqual(genesis.discoTimestamp,t)
        self.assertEqual(genesis.arrivTimestamp,s)
        self.assertTrue(genesis.parent is None)
        self.assertEqual(genesis.diff,diff)
        
        bill.addBlock(genesis, mode, tr)
        
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertTrue(genesis.ident in bill.leaves)
        self.assertEqual(len(bill.miningIdents),1)
        self.assertEqual(genesis.ident, bill.miningIdents[0])
        self.assertEqual(bill.diff, 1.0)
        
        parent = genesis.ident
        oldDiff = bill.diff
        i = 1
        
        while len(bill.blocks)<2016*i-1:
            newName = newIdent(len(bill.blocks))
            t += deltaT
            s += deltaT
            diff = bill.diff
            params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
            newBlock = Block(params)
            bill.addBlock(newBlock, mode, tr)
            parent = newName
            
        # Just one more block and difficulty should recompute.
        print("Just one more block and difficulty should recompute.")
        self.assertEqual(bill.diff, oldDiff)
        newName = newIdent(len(bill.blocks))
        t += deltaT
        s += deltaT
        diff = bill.diff
        params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
        newBlock = Block(params)
        bill.addBlock(newBlock, mode, tr) 
        parent = newName
        self.assertEqual(bill.diff, oldDiff)
          
        oldDiff = bill.diff
        i += 1
        
        while len(bill.blocks)<2016*i-1:
            newName = newIdent(len(bill.blocks))
            t += deltaT
            s += deltaT
            diff = bill.diff
            params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
            newBlock = Block(params)
            
            bill.addBlock(newBlock, mode, tr)
            parent = newName
        
        # Just one more block and difficulty should recompute.
        print("Just one more block and difficulty should again recompute.")
        self.assertEqual(bill.diff, oldDiff)
        newName = newIdent(len(bill.blocks))
        t += deltaT
        s += deltaT
        diff = bill.diff
        params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
        newBlock = Block(params)
        bill.addBlock(newBlock, mode, tr) 
        parent = newName
        self.assertEqual(bill.diff, oldDiff)
          
        oldDiff = bill.diff
        i += 1
        a = 1.1
        b = 1.0/a
        
        # If blocks arrive slightly further apart, difficulty should drop.
        while len(bill.blocks)<2016*i-1:
            newName = newIdent(len(bill.blocks))
            t += deltaT*a
            s += deltaT*a
            diff = bill.diff
            params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
            newBlock = Block(params)
            
            bill.addBlock(newBlock, mode, tr)
            parent = newName
            
        print("Just one more block and difficulty will go down.")
        
        self.assertEqual(bill.diff, oldDiff)
        newName = newIdent(len(bill.blocks))
        t += deltaT*a
        s += deltaT*a
        diff = bill.diff
        params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
        newBlock = Block(params)
        bill.addBlock(newBlock, mode, tr) 
        parent = newName
        err = abs(bill.diff - oldDiff*b)
        self.assertTrue(err*err < 10**-15)
        oldDiff = bill.diff
        i += 1
            
         
        # If blocks then arrive on target, difficulty should freeze.
        a = 1.0
        b = 1.0/a
        while len(bill.blocks)<2016*i-1:
            newName = newIdent(len(bill.blocks))
            t += deltaT*a
            s += deltaT*a
            diff = bill.diff
            params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
            newBlock = Block(params)
            
            bill.addBlock(newBlock, mode, tr)
            parent = newName
            
        self.assertEqual(bill.diff, oldDiff)
        newName = newIdent(len(bill.blocks))
        t += deltaT*a
        s += deltaT*a
        diff = bill.diff
        params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
        newBlock = Block(params)
        bill.addBlock(newBlock, mode, tr) 
        parent = newName
        self.assertEqual(bill.diff, oldDiff)
        oldDiff = bill.diff
        i += 1
        
        # If blocks arrive too close together, difficulty should increase.
        a = 0.9
        b = 1.0/a
        while len(bill.blocks)<2016*i-1:
            newName = newIdent(len(bill.blocks))
            t += deltaT*a
            s += deltaT*a
            diff = bill.diff
            params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
            newBlock = Block(params)
            
            bill.addBlock(newBlock, mode, tr)
            parent = newName
            
        print("Just one more block and difficulty should go up.")
        self.assertEqual(bill.diff, oldDiff)
        newName = newIdent(len(bill.blocks))
        t += deltaT*a
        s += deltaT*a
        diff = bill.diff
        params = {"ident":newName, "disco":t, "arriv":s, "parent":parent, "diff":diff}
        newBlock = Block(params)
        bill.addBlock(newBlock, mode, tr) 
        parent = newName
        err = abs(bill.diff - oldDiff*b)
        self.assertTrue(err*err < 10**-15)
    
            
        
       
        
#suite = unittest.TestLoader().loadTestsFromTestCase(Test_Blockchain)
#unittest.TextTestRunner(verbosity=1).run(suite)
