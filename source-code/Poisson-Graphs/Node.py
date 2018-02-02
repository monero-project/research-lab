from Blockchain import *

class Node(object):
    '''
    Node object. params [identity, blockchain (data), verbosity, difficulty]
    '''
    def __init__(self, params={}):
        try:
            assert len(params)==4
        except AssertionError:
            print("Error, Tried to create malformed node.")
        else:
            self.ident = params["ident"]
            self.data = params["data"]
            self.diff = params["diff"]
            self.verbose = params["verbose"]
            self.edges = {}
        
    def updateBlockchain(self, incBlocks, diffUpdateRate=1, mode="Nakamoto", targetRate=1.0/1209600.0):
        # dataToUpdate shall be a dictionary of block identities (as keys) and their associated blocks (as values)
        # to be added to the local data. We assume difficulty scores have been reported honestly for now.
        
        # Stash a copy of incoming blocks so removing keys won't shrink the size of the dictionary over which
        # we are looping.
        
        if self.verbose:
            print("\t\t Updating blockchain.")
        
        if self.verbose:
            print("\t\tAdding incoming blocks in order of parentage")
        
        if self.verbose:
            print("\t\tFirst step. incBlocks has " + str(len(incBlocks)) + " entries.")
        tempData = copy.deepcopy(incBlocks)
        
        if self.verbose:
            print("\t\t Now tempData has " + str(len(tempData)) + " entries.")
            
        for key in incBlocks.blocks:
            if key in self.data["blockchain"].blocks:
                del tempData[key]
            elif incBlocks.blocks[key].parent in self.data["blockchain"].blocks or incBlocks[key].parent is None:
                self.data["blockchain"].addBlock(incBlocks.blocks[key])
                #if len(self.data["blockchain"]) % diffUpdateRate == 0:
                #    self.updateDifficulty(mode, targetRate)
                del tempData[key]
        incBlocks = copy.deepcopy(tempData)
        
        if self.verbose:
            print("\t\t Now incBlocks has " + str(len(incBlocks.blocks)) + " entries.")
        
        if self.verbose:
            print("\t\tRemaining steps (while loop)")
            
        while len(incBlocks)>0:
            if self.verbose:
                print("\t\t Now tempData has " + str(len(tempData.blocks)) + " entries.")
            for key in incBlocks:
                if key in self.data["blockchain"].blocks:
                    del tempData[key]
                elif incBlocks.blocks[key].parent in self.data["blockchain"].blocks:
                        self.data["blockchain"].addBlock(incBlocks.blocks[key])
                        del tempData[key]
            incBlocks = copy.deepcopy(tempData)
            if self.verbose:
                print("\t\t Now incBlocks has " + str(len(incBlocks)) + " entries.")
        
            
    def updateDifficulty(self, mode="Nakamoto", targetRate=1.0/1209600.0):
        # Compute the difficulty of the next block
        # Note for default, targetRate = two weeks/period, seven days/week, 24 hours/day, 60 minutes/hour, 60 seconds/minute) = 1209600 seconds/period
        if mode=="Nakamoto":
            # Use MLE estimate of poisson process, compare to targetRate, update by multiplying by resulting ratio.
            count = 2016
            bc = self.data["blockchain"]
            ident = bc.miningIdent
            topTime = copy.deepcopy(bc.blocks[ident].discoTimestamp)
            parent = bc.blocks[ident].parent
            count = count - 1
            touched = False
            while count > 0 and parent is not None:
                ident = copy.deepcopy(parent)
                parent = bc.blocks[ident].parent
                count = count - 1
                touched = True
            if not touched:
                mleDiscoRate = targetRate
            else:
                botTime = copy.deepcopy(bc.blocks[ident].discoTimestamp)
            
                # Algebra is okay:
                assert 0 <= 2016 - count and 2016 - count < 2017
                assert topTime != botTime
                # MLE estimate of arrivals per second:
                mleDiscoRate = float(2016 - count)/float(topTime - botTime)
                mleDiscoRate = abs(mleDiscoRate) 
                # Rate must be positive... so the MLE for block arrival rate
                # assuming a Poisson process _is not even well-defined_ as
                # an estimate for block arrival rate assuming timestamps are
                # inaccurately reported!
                
                # We use it nonetheless.
                
            # How much should difficulty change?
            self.diff = self.diff*(mleDiscoRate/targetRate)
            
        elif mode=="vanSaberhagen":
            # Similar to above, except use 1200 blocks, discard top 120 and bottom 120 after sorting.
            # 4 minute blocks in the original cryptonote, I believe... targetRate = 1.0/
            # 4 minutes/period, 60 seconds/minute ~ 240 seconds/period
            assert targetRate==1.0/240.0
            count = 1200
            ident = self.data.miningIdent
            bl = []
            bl.append(copy.deepcopy(self.data.blocks[ident].discoTimestamp))
            parent = self.data.blocks[ident].parent
            count = count - 1
            while count > 0 and parent is not NOne:
                ident = copy.deepcopy(parent)
                bl.append(copy.deepcopy(self.data.blocks[ident].discoTimestamp))
                parent = self.data.blocks[ident].parent
                count = count-1
            # sort    
            bl = sorted(bl)
            
            # remove outliers
            bl = bl[120:-120]
            
            # get topTime and botTime
            topTime = bl[-1]
            botTime = bl[0]
            
            # Assert algebra will work
            assert 0 <= 960 - count and 960 - count < 961
            assert topTime > botTime
            
            # Sort of the MLE: # blocks/difference in reported times
            # But not the MLE, since the reported times may not be 
            # the actual times, the "difference in reported times" != 
            # "ground truth difference in block discoery times" in general 
            naiveDiscoRate = (960 - count)/(topTime - botTime)
            
            # How much should difficulty change?
            self.diff = self.diff*(naiveDiscoRate/targetRate)
            
        elif mode=="MOM:expModGauss":
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
            assert targetRate==1.0/120.0
            count = 1200
            ident = self.data.miningIdent
            bl = []
            bl.append(copy.deepcopy(self.data.blocks[ident].discoTimestamp))
            parent = self.data.blocks[ident].parent
            count = count - 1
            while count > 0 and parent is not NOne:
                ident = copy.deepcopy(parent)
                bl.append(copy.deepcopy(self.data.blocks[ident].discoTimestamp))
                parent = self.data.blocks[ident].parent
                count = count-1
            sk   = skew(bl)
            va   = var(bl)
            stdv = sqrt(va)
            lam  = (1.0/stdv)*(2.0/sk)**(1.0/3.0)
            self.diff = self.diff*(lam/targetRate)
        else:
            print("Error, invalid difficulty mode entered.")
            
    def propagate(self, t, blockIdent):
        for edgeIdent in self.edges:
            e = self.edges[edgeIdent]
            l = e.data["length"]
            toa = t + l
            mIdent = e.getNeighbor(self.ident)
            m = e.nodes[mIdent]
            bc = m.data["blockchain"]
            if blockIdent not in bc.blocks:
                pB = e.data["pendingBlocks"]
                pendingIdent = newIdent(len(pB))
                mybc = self.data["blockchain"]
                pendingDat = {"timeOfArrival":toa, "destIdent":mIdent, "block":mybc.blocks[blockIdent]}
                pB.update({pendingIdent:pendingDat})
       

class Test_Node(unittest.TestCase):
    def test_node(self):
        verbose = True
        nellyIdent = newIdent(0)
        bill = Blockchain([], verbosity=verbose)
        
        name = newIdent(0)
        t = time.time()
        s = t+1
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
        genesis = Block(params)
        bill.addBlock(genesis)
        
        time.sleep(10)
        
        name = newIdent(1)
        t = time.time()
        s = t+1
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":genesis.ident, "diff":diff}
        blockA = Block(params)
        bill.addBlock(blockA)
        
        # Nodes need an identity and a blockchain object and verbosity and difficulty
        nodeData = {"blockchain":bill, "intensity":random.random(), "offset":random.random()}
        params = {"ident":name, "data":nodeData, "diff":diff, "verbose":verbose}
        nelly = Node(params)
        nelly.updateDifficulty(mode="Nakamoto")
        
        time.sleep(9)
        
        name = newIdent(len(nelly.data))
        t = time.time()
        s = t + 1
        params = {"ident":name, "disco":t, "arriv":s, "parent":blockA.ident, "diff":diff}
        blockB = Block(params)
        nelly.updateBlockchain({blockB.ident:blockB})
        
        time.sleep(8)
        
        name = newIdent(len(nelly.data))
        t = time.time()
        s = t + 1
        params = {"ident":name, "disco":t, "arriv":s, "parent":blockA.ident, "diff":diff}
        blockC = Block(params)
        nelly.updateBlockchain({blockC.ident:blockC})
        
        time.sleep(1)
        name = newIdent(len(nelly.data))
        t = time.time()
        s = t + 1
        params = {"ident":name, "disco":t, "arriv":s, "parent":blockC.ident, "diff":diff}
        blockD = Block(params)
        nelly.updateBlockchain({blockD.ident:blockD})
        
        time.sleep(7)
        name = newIdent(len(nelly.data))
        t = time.time()
        s = t + 1
        params = {"ident":name, "disco":t, "arriv":s, "parent":blockD.ident, "diff":diff}
        blockE = Block(params)
        nelly.updateBlockchain({blockE.ident:blockE})
        
        
        time.sleep(6)
        name = newIdent(len(nelly.data))
        t = time.time()
        s = t + 1
        params = {"ident":name, "disco":t, "arriv":s, "parent":blockE.ident, "diff":diff}
        blockF = Block(params)
        nelly.updateBlockchain({blockF.ident:blockF})
        
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_Node)
unittest.TextTestRunner(verbosity=1).run(suite)
       
