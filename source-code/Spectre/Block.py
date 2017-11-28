import unittest
import math
import numpy as np
import copy
from collections import deque
import time

class Block(object):
    """ Fundamental object. Contains dict of blockIDs:(parent blocks) """
    def __init__(self):
        self.id = ""           # string
        self.timestamp = None  # format tbd
        self.data = None       # payload
        self.parents = {}      # block ID : pointer to block
        self.children = {}     # block ID : pointer to block
    def addChild(self, childIn):
        if childIn not in self.children:
            self.children.update({childIn.id:childIn})
    def addChildren(self, childrenIn):
        for child in childrenIn:
            self.addChild(childrenIn[child])
    def addParent(self, parentIn):
        if parentIn not in self.parents:
            self.parents.update({parentIn.id:parentIn})
    def addParents(self, parentsIn):
        for parent in parentsIn:
            self.addParent(parentsIn[parent])
    
    
class Test_Block(unittest.TestCase):
    def test_Block(self):
        b0 = Block()
        b0.id = "0"
        self.assertTrue(b0.data is None)
        self.assertTrue(len(b0.parents)==0)
        
        b1 = Block()
        b1.parents.update({"0":b0})
        b1.id = "1"
        for parentID in b1.parents:
            b1.parents[parentID].children.update({b1.id:b1})
        self.assertTrue(b1.data is None)
        self.assertTrue(len(b1.parents)==1)
        self.assertTrue("0" in b1.parents)
        
        b2 = Block()
        b2.parents.update({"0":b0})
        b2.id = "2"
        for parentID in b2.parents:
            b2.parents[parentID].children.update({b2.id:b2})
        self.assertTrue(b2.data is None)
        self.assertTrue(len(b2.parents)==1)
        self.assertTrue("0" in b2.parents)

        b3 = Block()
        b3.parents.update({"1":b1, "2":b2})
        b3.id = "3" 
        for parentID in b3.parents:
            b3.parents[parentID].children.update({b3.id:b3})
        self.assertTrue(b3.data is None)
        self.assertTrue(len(b3.parents)==2)
        self.assertTrue("1" in b3.parents)
        self.assertTrue("2" in b3.parents)
        self.assertFalse("0" in b3.parents)

        b4 = Block()
        b4.parents.update({"2":b2})
        b4.id = "4"
        for parentID in b4.parents:
            b4.parents[parentID].children.update({b4.id:b4})
        self.assertTrue(b4.data is None)
        self.assertTrue(len(b4.parents)==1)
        self.assertTrue("2" in b4.parents)

suite = unittest.TestLoader().loadTestsFromTestCase(Test_Block)
unittest.TextTestRunner(verbosity=1).run(suite)

