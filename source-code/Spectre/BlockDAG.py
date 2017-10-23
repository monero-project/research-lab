from Block import *

class BlockDAG(object):
    """ Collection of >=1 block. Also tracks IDs of leaf blocks, adds new leaves. """
    def __init__(self):
        self.blocks = {}
        self.leaves = {}
        self.genBlock = None
    def startDAG(self, idIn=None, genBlockIn=None):
        if genBlockIn is not None:
            genesisBlock = genBlockIn
        else:
            genesisBlock = Block()
            if idIn is None:
                genesisBlock.setID(idIn="0")
            else:
                genesisBlock.setID(idIn)
        self.genBlock = genesisBlock
        self.blocks.update({self.genBlock.id:self.genBlock})
        self.leaves.update({self.genBlock.id:self.genBlock})
    def addLeaf(self, blockIn):
        self.blocks.update({blockIn.id:blockIn})
        self.leaves.update({blockIn.id:blockIn})
        for parent in blockIn.parents:
            if parent in self.leaves:
                del self.leaves[parent]


class Test_BlockDAG(unittest.TestCase):
    def test_BlockDAG(self):
        dag = BlockDAG()
        dag.startDAG()
        self.assertTrue("0" in dag.blocks)
        self.assertTrue("0" in dag.leaves)
        self.assertTrue(len(dag.blocks)==1)
        self.assertTrue(len(dag.leaves)==1)
        b0 = dag.genBlock

        b1 = Block()
        b1.setParents(parentList={"0":b0})
        b1.setID("1")
        dag.addLeaf(b1)
        self.assertTrue("1" in dag.blocks)
        self.assertTrue("1" in dag.leaves)
        self.assertTrue("0" not in dag.leaves)
        self.assertTrue(len(dag.blocks)==2)
        self.assertTrue(len(dag.leaves)==1)

        
        b2 = Block()
        b2.setParents(parentList={"0":b0})
        b2.setID("2")
        dag.addLeaf(b2)
        
        b3 = Block()
        b3.setParents(parentList={"1":b1, "2":b2})
        b3.setID("3") 
        dag.addLeaf(b3)

        b4 = Block()
        b4.setParents(parentList={"2":b2})
        b4.setID("4")
        dag.addLeaf(b4)

        self.assertTrue("0" in dag.blocks and "1" in dag.blocks and "2" in dag.blocks and "3" in dag.blocks and "4" in dag.blocks)
        self.assertTrue("3" in dag.leaves and "4" in dag.leaves)
        self.assertTrue(len(dag.blocks)==5 and len(dag.leaves)==2)
                

suite = unittest.TestLoader().loadTestsFromTestCase(Test_BlockDAG)
unittest.TextTestRunner(verbosity=1).run(suite)

