import unittest
import math
import numpy as np
import copy
from collections import deque
import time

class Block(object):
    """ Fundamental object. Contains dict of blockIDs:(parent blocks) """
    def __init__(self, idIn=None, parentList=None):
        self.parents = {}
        self.id = ""
        self.data = None
    def setParents(self, parentList=None):
        if parentList is not None:
            self.parents = copy.deepcopy(parentList)
    def setID(self, idIn = None):    
        if idIn is not None:
            self.id = copy.deepcopy(idIn)
    
class Test_Block(unittest.TestCase):
    def test_Block(self):
        b0 = Block()
        b0.setParents()
        b0.setID("0")
        self.assertTrue(b0.data is None)
        self.assertTrue(len(b0.parents)==0)
        
        b1 = Block()
        b1.setParents(parentList={"0":b0})
        b1.setID("1")
        self.assertTrue(b1.data is None)
        self.assertTrue(len(b1.parents)==1)
        self.assertTrue("0" in b1.parents)
        
        b2 = Block()
        b2.setParents(parentList={"0":b0})
        b2.setID("2")
        self.assertTrue(b2.data is None)
        self.assertTrue(len(b2.parents)==1)
        self.assertTrue("0" in b2.parents)

        b3 = Block()
        b3.setParents(parentList={"1":b1, "2":b2})
        b3.setID("3") 
        self.assertTrue(b3.data is None)
        self.assertTrue(len(b3.parents)==2)
        self.assertTrue("1" in b3.parents)
        self.assertTrue("2" in b3.parents)
        self.assertFalse("0" in b3.parents)

        b4 = Block()
        b4.setParents(parentList={"2":b2})
        b4.setID("4")
        self.assertTrue(b4.data is None)
        self.assertTrue(len(b4.parents)==1)
        self.assertTrue("2" in b4.parents)

suite = unittest.TestLoader().loadTestsFromTestCase(Test_Block)
unittest.TextTestRunner(verbosity=1).run(suite)

