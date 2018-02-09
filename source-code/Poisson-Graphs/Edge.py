from Node import *
                
class Edge(object):
    '''
    Edge object. Has an identity, some data, and a dict of nodes.
    '''
    def __init__(self, params):
        try:
            assert len(params)==3
        except AssertionError:
            print("Error, tried to create mal-formed edge.")
        else:
            self.ident = params[0]
            self.data = params[1]
            self.verbose = params[2]
            self.nodes = {}
        
    def getNeighbor(self, nodeIdent):
        # Given one node identity, check that the node
        # identity is in the edge's node list and 
        # return the identity of the other adjacent node.
        result = (nodeIdent in self.nodes)
        if result:
            for otherIdent in self.nodes:
                if otherIdent != nodeIdent:
                    result = otherIdent
        assert result in self.nodes
        return result
        
class Test_Edge(unittest.TestCase):
    def test_e(self):
        params = None
        nelly = Node(params)
        milly = Node(params)
        ed = Edge(params)
        ed.nodes.update({nelly.ident:nelly, milly.ident:milly})
        self.assertEqual(len(self.nodes),2)
        
        
#suite = unittest.TestLoader().loadTestsFromTestCase(Test_Edge)
#unittest.TextTestRunner(verbosity=1).run(suite)
