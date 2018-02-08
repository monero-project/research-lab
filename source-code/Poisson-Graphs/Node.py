from Blockchain import *
import copy

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
        # incBlocks shall be a dictionary of block identities (as keys) and their associated blocks (as values)
        # to be added to the local data. We assume difficulty scores have been reported honestly for now.
        
        if self.verbose:
            print("\t\t Updating blockchain.")
        
        if self.verbose:
            print("\t\tAdding incoming blocks in order of parentage")
        
        if self.verbose:
            print("\t\tFirst step. incBlocks has " + str(len(incBlocks)) + " entries.")
        tempData = copy.deepcopy(incBlocks)
        
        if self.verbose:
            print("\t\t Now tempData has " + str(len(tempData)) + " entries.")
            
        for key in incBlocks:
            if key in self.data["blockchain"].blocks:
                del tempData[key]
            elif incBlocks[key].parent in self.data["blockchain"].blocks or incBlocks[key].parent is None:
                self.data["blockchain"].addBlock(incBlocks[key])
                self.data["blockchain"].whichLeaf()
                #if len(self.data["blockchain"]) % diffUpdateRate == 0:
                #    self.updateDifficulty(mode, targetRate)
                del tempData[key]
        incBlocks = copy.deepcopy(tempData)
        
        if self.verbose:
            print("\t\t Now incBlocks has " + str(len(incBlocks)) + " entries.")
        
        if self.verbose:
            print("\t\tRemaining steps (while loop)")
            
        while len(incBlocks)>0:
            if self.verbose:
                print("\t\t Now tempData has " + str(len(tempData.blocks)) + " entries.")
            for key in incBlocks:
                if key in self.data["blockchain"].blocks:
                    del tempData[key]
                elif incBlocks[key].parent in self.data["blockchain"].blocks:
                        self.data["blockchain"].addBlock(incBlocks[key])
                        self.data["blockchain"].whichLeaf()
                        del tempData[key]
            incBlocks = copy.deepcopy(tempData)
            if self.verbose:
                print("\t\t Now incBlocks has " + str(len(incBlocks)) + " entries.")
        
            
    def updateDifficulty(self, mode="Nakamoto", targetRate=1.0/1209600.0):
        # Compute the difficulty of the next block
        # Note for default, targetRate = two weeks/period, seven days/week, 24 hours/day, 60 minutes/hour, 60 seconds/minute) = 1209600 seconds/period
        if mode=="Nakamoto":
            # Use MLE estimate of poisson process, compare to targetRate, update by multiplying by resulting ratio.
            if self.verbose:
                print("Beginning update of difficulty with Nakamoto method")
            count = 2016
            bc = self.data["blockchain"]
            if self.verbose:
                print("Checking that blockchain is 2016*n blocks long and some mining identity has been set")
            if len(bc.blocks) % 2016 == 0 and len(bc.miningIdents) > 0:
                
                ident = random.choice(bc.miningIdents)
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
                    assert topTime != botTime
                    
                    # MLE estimate of arrivals per second:
                    mleDiscoRate = float(2015)/float(topTime - botTime)
                    
                    # Rates can't be negative, but this estimate could be (although it's highly unlikely given Bitcoin's standard choices
                    # of difficulty update rate, etc.
                    mleDiscoRate = abs(mleDiscoRate) 
                    
                    if self.verbose:
                        print("MLE disco rate = " + str(mleDiscoRate) + " and targetRate = " + str(targetRate))
                    # Rate must be positive... so the MLE for block arrival rate
                    # assuming a Poisson process _is not even well-defined_ as
                    # an estimate for block arrival rate assuming timestamps are
                    # inaccurately reported!
                    
                    # We use it nonetheless.
                
                if self.verbose:
                    print("MLE discovery rate = " + str(mleDiscoRate))
                    print("Difficulty before adjustment = " + str(self.diff))
                
                # Update difficulty multiplicatively
                self.diff = self.diff*mleDiscoRate/targetRate
                
                if self.verbose:
                    print("Difficulty after adjustment = ", str(self.diff))
                
        elif mode=="vanSaberhagen":
            # Similar to above, except use 1200 blocks, discard top 120 and bottom 120 after sorting.
            # 4 minute blocks in the original cryptonote, I believe... targetRate = 1.0/
            # 4 minutes/period, 60 seconds/minute ~ 240 seconds/period
            # assert targetRate==1.0/240.0
            count = 1200
            bc = self.data["blockchain"]
            bc.whichLeaf()
            assert self.diff != 0.0
            if len(bc.blocks) > 120:
                assert type(bc.miningIdents)==type([])
                assert len(bc.miningIdents) > 0
                ident = random.choice(bc.miningIdents)
                bl = []
                bl.append(copy.deepcopy(bc.blocks[ident].discoTimestamp))
                parent = bc.blocks[ident].parent
                count = count - 1
                while count > 0 and parent is not None:
                    ident = copy.deepcopy(parent)
                    bl.append(copy.deepcopy(bc.blocks[ident].discoTimestamp))
                    parent = bc.blocks[ident].parent
                    count = count-1
                # sort    
                bl = sorted(bl)
                assert len(bl)<=1200
                
                #print("Sample size = " + str(len(bl)))
                # remove 10 and 90 %-iles
                numOutliers = round(len(bl)/5)//2
                assert numOutliers <= 120
                #print("Number of outliers = " + str(numOutliers))
                if numOutliers > 0:
                    bl = bl[numOutliers:-numOutliers]
                #print("New Sample Size = " + str(len(bl)))
                    
                
                # get topTime and botTime
                if self.verbose:
                    print("bl[0] = " + str(bl[0]) + ",\tbl[-1] = " + str(bl[-1]))
                topTime = bl[-1]
                botTime = bl[0]
                if self.verbose:
                    print("list of timestamps = " + str(bl))
                    print("topTime = " + str(bl[-1]))
                    print("botTime = " + str(bl[0]))
                
                # Assert algebra will work
                # 1200 - 2*120 = 1200 - 240 = 960
                assert 0 < len(bl) and len(bl) < 961
                assert topTime - botTime >= 0.0
                
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
            bc = self.data["blockchain"]
            if len(bc.miningIdents) > 0:
                ident = random.choice(bc.miningIdents)
            
            bl = []
            bl.append(copy.deepcopy(bc.blocks[ident].discoTimestamp))
            parent = bc.blocks[ident].parent
            count = count - 1
            while count > 0 and parent is not None:
                ident = copy.deepcopy(parent)
                bl.append(copy.deepcopy(bc.blocks[ident].discoTimestamp))
                parent = bc.blocks[ident].parent
                count = count-1
            if len(bl) > 120:
                sk   = skew(bl)
                va   = var(bl)
                stdv = sqrt(va)
                lam  = (1.0/stdv)*(2.0/sk)**(1.0/3.0)
            else:
                lam = targetRate # we will not change difficulty unless we have at least 120 blocks of data (arbitrarily selected)
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
    # TODO test each method separately
    '''def test_nakamoto(self):
        print("Beginning test of Nakamoto difficulty adjustment")
        print("Setting initial values")
        target = 100.0 # rate = blocks/s
        verbose = False
        deltaT = 1.0/target # forced wait time
        arrivalList = []
        mode="Nakamoto"
        
        print("Generating node")
        nellyIdent = newIdent(0)
        offset = random.random()
        intensity = random.random()
        
        print("Generating initial blockchain")
        # Create a new initial blockchain object
        bill = Blockchain([], verbosity=verbose)
        name = newIdent(0)
        t = time.time()
        t += offset
        arrivalList.append(t)
        s = t+random.random()
        diff = 1.0
        oldDiff = copy.deepcopy(diff)
        params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
        genesis = Block(params)
        print("Adding block")
        bill.addBlock(genesis)
        bill.whichLeaf()
        
        # Check that it consists only of the genesis block
        self.assertTrue(len(bill.blocks)==1)
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertTrue(genesis.parent is None)
        
        print("Finish creating node")
        # Create node with this blockchain.
        nodeData = {"blockchain":bill, "intensity":intensity, "offset":offset}
        params = {"ident":nellyIdent, "data":nodeData, "diff":diff, "verbose":verbose}
        nelly = Node(params)
        
        # Check node creation worked
        self.assertEqual(nelly.ident, nellyIdent)
        self.assertEqual(nelly.data["blockchain"], bill)
        self.assertEqual(nelly.diff, diff)
        self.assertEqual(nelly.data["intensity"], intensity)
        self.assertEqual(nelly.data["offset"], offset)
        
        # Sleep and add a block on top of genesis
        if verbose:
            print("sleeping")
        time.sleep(deltaT)
        
        print("Giving genesis block a child")
        name = newIdent(1)
        t = time.time()
        t += nelly.data["offset"]
        arrivalList.append(t)
        s = t+random.random()
        diff = oldDiff
        params = {"ident":name, "disco":t, "arriv":s, "parent":genesis.ident, "diff":diff}
        blockA = Block(params)
        nelly.updateBlockchain({blockA.ident:blockA})
        oldIdent = blockA.ident
        
        # Check this worked
        self.assertEqual(len(nelly.data["blockchain"].blocks),2)
        self.assertTrue(blockA.ident in nelly.data["blockchain"].blocks)
        self.assertTrue(genesis.ident in nelly.data["blockchain"].blocks)
        self.assertEqual(genesis.ident, nelly.data["blockchain"].blocks[blockA.ident].parent)
        
        print("Updating difficulty")
        # Update the difficulty score
        nelly.updateDifficulty(mode, targetRate = target) # With only two blocks, nothing should change.
        self.assertEqual(nelly.diff, oldDiff)
        
        # Print regardless of verbosity:
        print("Now generating first difficulty adjustment period.")
        
        # Now we are going to fast forward to right before the first difficulty adjustment.
        N = len(nelly.data["blockchain"].blocks)
        while(N < 2015):
            if N % 100 == 0:
                print("\tN=" + str(N))
            name = newIdent(N)
            t = time.time()
            t += nelly.data["offset"]
            arrivalList.append(t)
            s = t+random.random()
            diff = nelly.diff
            oldDiff = diff
            params = {"ident":name, "disco":t, "arriv":s, "parent":oldIdent, "diff":diff}
            oldIdent = copy.deepcopy(name)
            block = Block(params)
            nelly.updateBlockchain({block.ident:block})
            
            # Check this worked
            self.assertEqual(len(nelly.data["blockchain"].blocks),N+1)
            self.assertTrue(block.ident in nelly.data["blockchain"].blocks)
            
            # Update the difficulty score
            nelly.updateDifficulty(mode, targetRate = target) # With N < 2016, nothing should change.
            self.assertEqual(nelly.diff, oldDiff)
            N = len(nelly.data["blockchain"].blocks)
            time.sleep(deltaT)
            
        name = newIdent(N)
        t = time.time()
        t += nelly.data["offset"]
        arrivalList.append(t)
        s = t+random.random()
        diff = oldDiff
        params = {"ident":name, "disco":t, "arriv":s, "parent":oldIdent, "diff":diff}
        block = Block(params)
        nelly.updateBlockchain({block.ident:block})
        
        # Check this worked
        self.assertEqual(len(nelly.data["blockchain"].blocks),N+1)
        self.assertTrue(block.ident in nelly.data["blockchain"].blocks)
        
        # Update the difficulty score
        nelly.updateDifficulty(mode, targetRate = target) # With N < 2016, nothing should change.
        # Note: 2016 blocks is 2015 block inter-arrival times.
        expRatioNumerator = float(2015)/(arrivalList[-1] - arrivalList[-2016])
        expRatio = expRatioNumerator/target
        expDiff = oldDiff*expRatio
        self.assertEqual(nelly.diff, expDiff)
        
        # The following should fail, because our sample size is incorrect.
        expRatioNumerator = float(2016)/(arrivalList[-1] - arrivalList[-2016])
        expRatio = expRatioNumerator/target
        expDiff = oldDiff*expRatio
        self.assertFalse(nelly.diff - expDiff == 0.0)
        
        
        # Print regardless of verbosity:
        print("Now generating second difficulty adjustment period.")
        
        # Now we are going to fast forward to right before the next difficulty adjustment.
        # This time, though, we are going to re-set the block inter-arrival time deltaT
        # to half. This should drive difficulty up.
        lastDifficultyScore = copy.deepcopy(nelly.diff)
        N = len(nelly.data["blockchain"].blocks)
        while(N < 4031):
            if N % 100 == 0:
                print("\tN=" + str(N))
            name = newIdent(N)
            t = time.time()
            t += nelly.data["offset"]
            arrivalList.append(t)
            s = t+random.random()
            diff = nelly.diff
            oldDiff = diff
            params = {"ident":name, "disco":t, "arriv":s, "parent":oldIdent, "diff":diff}
            oldIdent = copy.deepcopy(name)
            block = Block(params)
            nelly.updateBlockchain({block.ident:block})
            
            # Check this worked
            self.assertEqual(len(nelly.data["blockchain"].blocks),N+1)
            self.assertTrue(block.ident in nelly.data["blockchain"].blocks)
            
            # Update the difficulty score
            nelly.updateDifficulty(mode, targetRate = target) # With N < 2016, nothing should change.
            self.assertEqual(nelly.diff, oldDiff)
            N = len(nelly.data["blockchain"].blocks)
            time.sleep(0.01*deltaT)
            
        # Now if we add a single new block, we should trigger difficulty adjustment.
        name = newIdent(N)
        t = time.time()
        t += nelly.data["offset"]
        arrivalList.append(t)
        s = t+random.random()
        diff = oldDiff
        params = {"ident":name, "disco":t, "arriv":s, "parent":oldIdent, "diff":diff}
        block = Block(params)
        nelly.updateBlockchain({block.ident:block})
        
        # Check this worked
        self.assertEqual(len(nelly.data["blockchain"].blocks),N+1)
        self.assertTrue(block.ident in nelly.data["blockchain"].blocks)
        
        # Update the difficulty score. 
        nelly.updateDifficulty(mode, targetRate = target)
        expRatioNumerator = float(2015)/(arrivalList[-1] - arrivalList[-2016])
        expRatio = expRatioNumerator/target
        expDiff = oldDiff*expRatio
        print("expRatio = " + str(expRatio) + ", lastDifficultyScore = " + str(lastDifficultyScore) + ", new difficulty = " + str(nelly.diff))
        self.assertEqual(nelly.diff, expDiff)
        '''
        
        
        
        
    def test_vs(self):
        print("Beginning test of vanSaberhagen difficulty adjustment.")
        print("Setting initial values")
        target = 10.0 # 1.0/240.0 # rate = blocks/s
        verbose = False
        deltaT = 1.0/target # forced wait time
        arrivalList = []
        mode="vanSaberhagen"
        
        print("Instantiating new node")
        nellyIdent = newIdent(0)
        offset = random.random()
        intensity = random.random()
        
        print("Creating new blockchain for new node")
        # Create a new initial blockchain object
        bill = Blockchain([], verbosity=verbose)
        name = newIdent(0)
        t = time.time()
        t += offset
        arrivalList.append(t)
        s = t+random.random()
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
        genesis = Block(params)
        print("Adding genesis block")
        bill.addBlock(genesis)
        bill.whichLeaf()
        
        # Check that it consists only of the genesis block
        self.assertTrue(len(bill.blocks)==1)
        self.assertTrue(genesis.ident in bill.blocks)
        self.assertTrue(genesis.parent is None)
        self.assertTrue(genesis.ident in bill.leaves)
        
        print("Making node")
        # Create node with this blockchain.
        nodeData = {"blockchain":bill, "intensity":intensity, "offset":offset}
        params = {"ident":nellyIdent, "data":nodeData, "diff":diff, "verbose":verbose}
        nelly = Node(params)
        
        # Check node creation worked
        self.assertEqual(nelly.ident, nellyIdent)
        self.assertEqual(nelly.data["blockchain"], bill)
        self.assertEqual(nelly.diff, diff)
        self.assertEqual(nelly.data["intensity"], intensity)
        self.assertEqual(nelly.data["offset"], offset)
        
        # Sleep and add a block on top of genesis
        if verbose:
            print("sleeping")
        time.sleep(deltaT)
        
        print("Give genesis a child")
        name = newIdent(1)
        t = time.time()
        t += nelly.data["offset"]
        arrivalList.append(t)
        s = t+random.random()
        oldDiff = copy.deepcopy(diff)
        diff = copy.deepcopy(nelly.diff)
        assert diff != 0.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":genesis.ident, "diff":diff}
        blockA = Block(params)
        nelly.updateBlockchain({blockA.ident:blockA})
        oldIdent = blockA.ident
        
        # Check this worked
        self.assertEqual(len(nelly.data["blockchain"].blocks),2)
        self.assertTrue(blockA.ident in nelly.data["blockchain"].blocks)
        self.assertTrue(genesis.ident in nelly.data["blockchain"].blocks)
        self.assertEqual(genesis.ident, nelly.data["blockchain"].blocks[blockA.ident].parent)
        
        # Update the difficulty score
        nelly.updateDifficulty(mode, targetRate = target) # With only two blocks, nothing should change.
        assert nelly.diff != 0.0
        self.assertEqual(nelly.diff, oldDiff)
        self.assertFalse(nelly.diff == -0.0)
        
        # Print regardless of verbosity:
        print("Now generating fulls sample size.")
        
        # Now we are going to fast forward to a "full sample size" period of time.
        N = len(nelly.data["blockchain"].blocks)
        while(N < 1200):
            name = newIdent(N)
            if N % 100 == 0:
                print("\tNow adding block N=" + str(N))
            t = time.time()
            t += nelly.data["offset"]
            arrivalList.append(t)
            s = t+random.random()
            oldDiff = copy.deepcopy(diff)
            diff = copy.deepcopy(nelly.diff)
            assert diff != 0.0
            params = {"ident":name, "disco":t, "arriv":s, "parent":oldIdent, "diff":diff}
            oldIdent = copy.deepcopy(name)
            block = Block(params)
            nelly.updateBlockchain({block.ident:block})
            
            # Check this worked
            self.assertEqual(len(nelly.data["blockchain"].blocks),N+1)
            self.assertTrue(block.ident in nelly.data["blockchain"].blocks)
            
            # Update the difficulty score
            nelly.updateDifficulty(mode, targetRate = target) # With N < 100, nothing should change.
            if N < 100:
                self.assertEqual(nelly.diff, oldDiff)
            N = len(nelly.data["blockchain"].blocks)
            time.sleep(0.5*deltaT)
            
        print("Adding one more block")
        name = newIdent(N)
        t = time.time()
        t += nelly.data["offset"]
        arrivalList.append(t)
        s = t+random.random()
        oldDiff = diff
        diff = nelly.diff
        assert diff != 0.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":oldIdent, "diff":nelly.diff}
        block = Block(params)
        nelly.updateBlockchain({block.ident:block})
        
        # Check this worked
        self.assertEqual(len(nelly.data["blockchain"].blocks),N+1)
        self.assertTrue(block.ident in nelly.data["blockchain"].blocks)
        
        # Update the difficulty score
        nelly.updateDifficulty(mode, targetRate = target) # With N < 2016, nothing should change.
        # Note: 2016 blocks is 2015 block inter-arrival times.
        print(str(arrivalList[-120]) + ", " + str(arrivalList[-1080]) + ", " + str(arrivalList[-120]-arrivalList[-1080]) + ", " + str(float(959)/(arrivalList[-120]-arrivalList[-1080]))+ ", " + str(float(float(959)/(arrivalList[-120]-arrivalList[-1080]))/float(target)))
        expRatioNumerator = float(959)/(arrivalList[-120] - arrivalList[-1080])
        expRatio = expRatioNumerator/target
        print(expRatio)
        expDiff = oldDiff*expRatio
        print(expDiff)
        print("expDiff = " + str(expDiff) + " and nelly.diff = " + str(nelly.diff))
        self.assertEqual(nelly.diff, expDiff)
        
        
        # Print regardless of verbosity:
        print("Now fast forwarding past the tail end of the last period..")
        # Now we are going to fast forward to right before the next difficulty adjustment.
        # This time, though, we are going to re-set the block inter-arrival time deltaT
        # to half. This should drive difficulty up.
        lastDifficultyScore = copy.deepcopy(nelly.diff)
        N = len(nelly.data["blockchain"].blocks)
        while(N < 1700):
            name = newIdent(N)
            t = time.time()
            t += nelly.data["offset"]
            arrivalList.append(t)
            s = t+random.random()
            diff = nelly.diff
            oldDiff = diff
            params = {"ident":name, "disco":t, "arriv":s, "parent":oldIdent, "diff":diff}
            oldIdent = copy.deepcopy(name)
            block = Block(params)
            nelly.updateBlockchain({block.ident:block})
            
            # Check this worked
            self.assertEqual(len(nelly.data["blockchain"].blocks),N+1)
            self.assertTrue(block.ident in nelly.data["blockchain"].blocks)
            
            # Update the difficulty score
            nelly.updateDifficulty(mode, targetRate = target) # With N < 2016, nothing should change.
            self.assertEqual(nelly.diff, oldDiff)
            N = len(nelly.data["blockchain"].blocks)
            time.sleep(0.01*deltaT)
            
        # Now if we add a single new block, we should trigger difficulty adjustment.
        name = newIdent(N)
        t = time.time()
        t += nelly.data["offset"]
        arrivalList.append(t)
        s = t+random.random()
        diff = oldDiff
        params = {"ident":name, "disco":t, "arriv":s, "parent":oldIdent, "diff":diff}
        block = Block(params)
        nelly.updateBlockchain({block.ident:block})
        
        # Check this worked
        self.assertEqual(len(nelly.data["blockchain"].blocks),N+1)
        self.assertTrue(block.ident in nelly.data["blockchain"].blocks)
        
        # Update the difficulty score. 
        nelly.updateDifficulty(mode, targetRate = target)
        expRatioNumerator = float(959)/(arrivalList[-120] - arrivalList[-1080])
        expRatio = expRatioNumerator/target
        expDiff = oldDiff*expRatio
        print("expRatio = " + str(expRatio) + ", lastDifficultyScore = " + str(lastDifficultyScore) + ", new difficulty = " + str(nelly.diff))
        self.assertEqual(nelly.diff, expDiff)
        
        
        
    def test_modexp(self):
        pass
        
    '''# Check this worked
        if mode == "Nakamoto":
            # In this case we take simple MLE estimate
            ratio = 1.0/abs(t1-t)
            print("Nakamoto mle = " + str(ratio))
            ratio = ratio/target
            print("Normalized = " + str(ratio))
            print("New diff = " + str(ratio*oldDiff))
            self.assertEqual(nelly.diff, ratio*oldDiff)
        elif mode == "vanSaberhagen":
            # In this case, with only 2 blocks, we just use simple MLE again
            ratio = 1.0/abs(t1-t)
            ratio = ratio/target
            self.assertEqual(nelly.diff, ratio*oldDiff)
        elif mode == "MOM:expModGauss":
            self.assertEqual(nelly.diff, 1.0)
            # With at least 120 blocks of data...
            #sk   = skew(bl)
            #va   = var(bl)
            #stdv = sqrt(va)
            #lam  = (1.0/stdv)*(2.0/sk)**(1.0/3.0)
            #self.diff = self.diff*(lam/targetRate)
            # Otherwise, set to 1.0
        else:
            print("what world are you living in?")
        
        if verbose:
            print("sleeping 1 seconds")
        time.sleep(deltaT/5.0)
        
        listOfTimes = [copy.deepcopy(t), copy.deepcopy(t1)]
        listOfBlocks = []
        
        N = len(nelly.data["blockchain"].blocks)
        lastIdent = blockA.ident
        
        bail = False
        while N < 10 and not bail:
            # Generate new block
            name = newIdent(N)
            t = time.time()
            t += nelly.data["offset"]
            s = t+random.random()
            oldDiff = copy.deepcopy(nelly.diff)
            print("Current difficulty = ", oldDiff)
            params = {"ident":name, "disco":t, "arriv":s, "parent":lastIdent, "diff":oldDiff}
            newBlock = Block(params)
            
            # Append new block to running list along with creation time
            listOfBlocks.append(newBlock)
            listOfTimes.append(copy.deepcopy(t))
            
            # Update nelly's blockchain with newBlock
            nelly.updateBlockchain({newBlock.ident:newBlock})
            lastIdent = name
            
            # Quick check that this worked:
            self.assertTrue(name in nelly.data["blockchain"].blocks)
            self.assertEqual(len(nelly.data["blockchain"].blocks), N+1)
            N = len(nelly.data["blockchain"].blocks)
        
            # Update difficulty
            nelly.updateDifficulty(mode, targetRate = 100.0)
            
            # Quick check that this worked:
            if mode == "Nakamoto":
                # In this case we take use top block and genesis block
                ratio = float(len(nelly.data["blockchain"].blocks) - 1)/(listOfTimes[-1] - listOfTimes[0])
                ratio = ratio / target
                self.assertEqual(nelly.diff, ratio*oldDiff)
                print("Hoped for difficulty = " + str(oldDiff*ratio) + ", and computed = " + str(nelly.diff))
            elif mode == "vanSaberhagen":
                # This case coincides with nakamoto until block 10
                ratio = float( len(nelly.data["blockchain"].blocks) - 1)/(listOfTimes[-1] - listOfTimes[0])
                ratio = ratio / target
                self.assertEqual(nelly.diff, ratio*oldDiff)
            elif mode == "MOM:expModGauss":
                self.assertEqual(nelly.diff, 1.0)
                # With at least 120 blocks of data...
                #sk   = skew(bl)
                #va   = var(bl)
                #stdv = sqrt(va)
                #lam  = (1.0/stdv)*(2.0/sk)**(1.0/3.0)
                #self.diff = self.diff*(lam/targetRate)
                # Otherwise, set to 1.0
            else:
                print("what world are you living in?")
            
            # Sleep a random time
            print("Sleeping a random sub-second, working on block " + str(N))
            deltaT = deltaT*ratio
            time.sleep(deltaT/5.0)
            
        while N < 120 and not bail:
            # Generate new block
            name = newIdent(N)
            t = time.time()
            t += nelly.data["offset"]
            s = t+random.random()
            oldDiff = copy.deepcopy(nelly.diff)
            params = {"ident":name, "disco":t, "arriv":s, "parent":lastIdent, "diff":oldDiff}
            newBlock = Block(params)
            
            # Append new block to running list along with creation time
            listOfBlocks.append(newBlock)
            listOfTimes.append(copy.deepcopy(t))
            
            # Update nelly's blockchain with newBlock
            nelly.updateBlockchain({newBlock.ident:newBlock})
            lastIdent = name
            
            # Quick check that this worked:
            self.assertTrue(name in nelly.data["blockchain"].blocks)
            self.assertEqual(len(nelly.data["blockchain"].blocks), N+1)
            N = len(nelly.data["blockchain"].blocks)
        
            # Update difficulty
            nelly.updateDifficulty(mode, targetRate = 100.0)
            
            # Quick check that this worked:
            if mode == "Nakamoto":
                # In this case we take use top block and genesis block
                ratio = float(len(nelly.data["blockchain"].blocks)-1)/(listOfTimes[-1] - listOfTimes[0])
                ratio = ratio / target
                self.assertEqual(nelly.diff, oldDiff*ratio)
                print("Hoped for difficulty = " + str(oldDiff*ratio) + ", and computed = " + str(nelly.diff))
            elif mode == "vanSaberhagen":
                # This case no longer coincides with Nakamoto...
                numOutliers = len(nelly.data["blockchain"].blocks)//10
                numOutliers = min(numOutliers, 120)
                ratio = float(len(nelly.data["blockchain"].blocks) - 2*numOutliers - 1)/(listOfTimes[-numOutliers] - listOfTimes[numOutliers])
                ratio = ratio / target
                self.assertEqual(nelly.diff, oldDiff*ratio)
            elif mode == "MOM:expModGauss":
                # With at least 120 blocks of data...
                count = 1200
                bl = []
                bl.append(copy.deepcopy(bc.blocks[lastIdent].discoTimestamp))
                parent = bc.blocks[lastIdent].parent
                count = count - 1
                while count > 0 and parent is not None:
                    ident = copy.deepcopy(parent)
                    bl.append(copy.deepcopy(bc.blocks[ident].discoTimestamp))
                    parent = bc.blocks[ident].parent
                    count = count-1
                if len(bl) > 120:
                    sk   = skew(bl)
                    va   = var(bl)
                    stdv = sqrt(va)
                    lam  = (1.0/stdv)*(2.0/sk)**(1.0/3.0)
                else:
                    lam = target
                ratio = lam/target
                self.assertEqual(nelly.diff, oldDiff*ratio)
                
            else:
                print("what world are you living in?")
            
            # Sleep a random time
            print("Sleeping a random sub-second, working on block " + str(N))
            deltaT = deltaT*ratio
            time.sleep(deltaT/5.0)
          
        while N < 2400 and not bail:
            # Generate new block
            name = newIdent(N)
            t = time.time()
            t += nelly.data["offset"]
            s = t+random.random()
            oldDiff = copy.deepcopy(nelly.diff)
            params = {"ident":name, "disco":t, "arriv":s, "parent":lastIdent, "diff":oldDiff}
            newBlock = Block(params)
            
            # Append new block to running list along with creation time
            listOfBlocks.append(newBlock)
            listOfTimes.append(copy.deepcopy(t))
            
            # Update nelly's blockchain with newBlock
            nelly.updateBlockchain({newBlock.ident:newBlock})
            lastIdent = name
            
            # Quick check that this worked:
            self.assertTrue(name in nelly.data["blockchain"].blocks)
            self.assertEqual(len(nelly.data["blockchain"].blocks), N+1)
            N = len(nelly.data["blockchain"].blocks)
        
            # Update difficulty
            nelly.updateDifficulty(mode, targetRate = 100.0)
            
            # Quick check that this worked:
            if mode == "Nakamoto":
                # In this case we take use top block and genesis block
                ratio = float(len(nelly.data["blockchain"].blocks)-1)/(listOfTimes[-1] - listOfTimes[0])
                ratio = ratio / target
                self.assertEqual(nelly.diff, oldDiff*ratio)
                print("Hoped for difficulty = " + str(oldDiff*ratio) + ", and computed = " + str(nelly.diff))
            elif mode == "vanSaberhagen":
                # This case no longer coincides with Nakamoto...
                numOutliers = len(nelly.data["blockchain"].blocks)//10
                numOutliers = min(numOutliers, 120)
                ratio = float(len(nelly.data["blockchain"].blocks) - 2*numOutliers - 1)/(listOfTimes[-numOutliers] - listOfTimes[numOutliers])
                ratio = ratio / target
                self.assertEqual(nelly.diff, ratio*oldDiff)
            elif mode == "MOM:expModGauss":
                # With at least 120 blocks of data...
                count = 1200
                bl = []
                bl.append(copy.deepcopy(bc.blocks[lastIdent].discoTimestamp))
                parent = bc.blocks[lastIdent].parent
                count = count - 1
                while count > 0 and parent is not None:
                    ident = copy.deepcopy(parent)
                    bl.append(copy.deepcopy(bc.blocks[ident].discoTimestamp))
                    parent = bc.blocks[ident].parent
                    count = count-1
                if len(bl) > 120:
                    sk   = skew(bl)
                    va   = var(bl)
                    stdv = sqrt(va)
                    lam  = (1.0/stdv)*(2.0/sk)**(1.0/3.0)
                else:
                    lam = targetRate 
                ratio = lam/targetRate
                self.assertEqual(nelly.diff, ratio*oldDiff)
                
            else:
                print("what world are you living in?")
            
            # Sleep a random time
            print("Sleeping a random sub-second, working on block " + str(N))
            deltaT = deltaT*ratio
            time.sleep(deltaT/5.0)
            
                   
        while N < 3600 and not bail:
            # Generate new block
            name = newIdent(N)
            t = time.time()
            t += nelly.data["offset"]
            s = t+random.random()
            oldDiff = nelly.diff
            params = {"ident":name, "disco":t, "arriv":s, "parent":lastIdent, "diff":oldDiff}
            newBlock = Block(params)
            
            # Append new block to running list along with creation time
            listOfBlocks.append(newBlock)
            listOfTimes.append(copy.deepcopy(t))
            
            # Update nelly's blockchain with newBlock
            nelly.updateBlockchain({newBlock.ident:newBlock})
            lastIdent = name
            
            # Quick check that this worked:
            self.assertTrue(name in nelly.data["blockchain"].blocks)
            self.assertEqual(len(nelly.data["blockchain"].blocks), N+1)
            N = len(nelly.data["blockchain"].blocks)
        
            # Update difficulty
            nelly.updateDifficulty(mode, targetRate = 100.0)
            
            # Quick check that this worked:
            if mode == "Nakamoto":
                # In this case we take use top block and genesis block
                ratio = float(2400)/(listOfTimes[-1] - listOfTimes[-2400])
                self.assertEqual(nelly.diff, ratio*oldDiff)
            elif mode == "vanSaberhagen":
                # This case no longer coincides with Nakamoto...
                numOutliers = len(nelly.data["blockchain"].blocks)//10
                numOutliers = min(numOutliers, 120)
                ratio = float(len(nelly.data["blockchain"].blocks) - 2*numOutliers)/(listOfTimes[-numOutliers] - listOfTimes[numOutliers])
                self.assertEqual(nelly.diff, ratio*oldDiff)
            elif mode == "MOM:expModGauss":
                # With at least 120 blocks of data...
                count = 1200
                bl = []
                bl.append(copy.deepcopy(bc.blocks[lastIdent].discoTimestamp))
                parent = bc.blocks[lastIdent].parent
                count = count - 1
                while count > 0 and parent is not None:
                    ident = copy.deepcopy(parent)
                    bl.append(copy.deepcopy(bc.blocks[ident].discoTimestamp))
                    parent = bc.blocks[ident].parent
                    count = count-1
                if len(bl) > 120:
                    sk   = skew(bl)
                    va   = var(bl)
                    stdv = sqrt(va)
                    lam  = (1.0/stdv)*(2.0/sk)**(1.0/3.0)
                else:
                    lam = targetRate 
                ratio = lam/targetRate
                self.assertEqual(nelly.diff, ratio*oldDiff)
                
            else:
                print("what world are you living in?")
            
            # Sleep a random time
            print("Sleeping a random sub-second, working on block " + str(N))
            deltaT = deltaT*ratio
            time.sleep(deltaT/5.0)'''
        
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_Node)
unittest.TextTestRunner(verbosity=1).run(suite)
       
