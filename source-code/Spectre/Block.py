import unittest
import math
import copy
from collections import deque
import time
import hashlib

class Block(object):
    """ 
        Fundamental object. Attributes:
            data    = payload dict with keys "timestamp" and "txns" and others
            ident   = string
            parents = dict {blockID : parentBlock}
        Functions:
            addParents      : takes dict {blockID : parentBlock} as input 
                              and updates parents to include.
            _recomputeIdent : recomputes identity
        Usage:
            b0 = Block(dataIn = stuff, parentsIn = None)
            b1 = Block(dataIn = otherStuff, parentsIn = { b0.ident : b0 })
        
    """
    def __init__(self, dataIn=None, parentsIn=[]):
        # Initialize with empty payload, no identity, and empty parents.
        self.data = dataIn
        self.ident = hash(str(0))
        assert type(parentsIn)==type([])
        self.parents = parentsIn
        self._recomputeIdent()
        
    def addParents(self, parentsIn=[]): # list of parentIdents
        if self.parents is None:
            self.parents = parentsIn
        else:
            self.parents = self.parents + parentsIn
        self._recomputeIdent()
        
    def _recomputeIdent(self):
        m = str(0) + str(self.data) + str(self.parents)
        self.ident = hash(m)
		
		
class Test_Block(unittest.TestCase):
    def test_Block(self):
		# b0 -> b1 -> {both b2, b3} -> b4... oh, and say  b3 -> b5 also
        b0 = Block()
        b0.data = {"timestamp" : time.time()}
        time.sleep(1)
        
        b1 = Block()
        b1.data = {"timestamp" : time.time(), "txns" : [1,2,3]}
        b1.addParents({b0.ident:b0}) # updateIdent called with addParent.
        time.sleep(1)
        
        b2 = Block()
        b2.data = {"timestamp" : time.time(), "txns" : None}
        b2.addParents({b1.ident:b1})
        time.sleep(1)
        
        b3 = Block()
        b3.data = {"timestamp" : time.time(), "txns" : None}
        b3.addParents({b1.ident:b1})
        time.sleep(1)
        
        b4 = Block()
        b4.data = {"timestamp" : time.time()} # see how sloppy we can be wheeee
        b4.addParents({b2.ident:b2, b3.ident:b3})
        time.sleep(1)
        
        b5 = Block()
        b5.data = {"timestamp" : time.time(), "txns" : "stuff" }
        b5.addParents({b3.ident:b3})
        
        self.assertTrue(len(b1.parents)==1 and b0.ident in b1.parents)
        self.assertTrue(len(b2.parents)==1 and b1.ident in b2.parents)
        self.assertTrue(len(b3.parents)==1 and b1.ident in b3.parents)
        self.assertTrue(len(b4.parents)==2)
        self.assertTrue(b2.ident in b4.parents and b3.ident in b4.parents)
        self.assertTrue(len(b5.parents)==1 and b3.ident in b5.parents)
        
        
#suite = unittest.TestLoader().loadTestsFromTestCase(Test_Block)
#unittest.TextTestRunner(verbosity=1).run(suite)
