import unittest, random, time

def newIdent(params):
    nonce = params
    # Generate new random identity.
    return hash(str(nonce) + str(random.random()))
 #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### ####
class Block(object):
    '''
    Each block has: an identity, a timestamp of discovery (possibly false), 
    has a timestamp of arrival at the local node (possibly unnecessary), a 
    parent block's identity, and a difficulty score.
    '''
    def __init__(self, params={}):
        self.ident = None
        self.discoTimestamp = None
        self.arrivTimestamp = None
        self.parent = None
        self.diff = None
        try:
            assert len(params)==5
        except AssertionError:
            print("Error in Block(): Tried to add a malformed block. We received params = " + str(params) + ", but should have had something of the form {\"ident\":ident, \"disco\":disco, \"arriv\":arriv, \"parent\":parent, \"diff\":diff}.")
        self.ident = params["ident"]
        self.discoTimestamp = params["disco"]
        self.arrivTimestamp = params["arriv"]
        self.parent = params["parent"]
        self.diff = params["diff"]
        
class Test_Block(unittest.TestCase):
    def test_b(self):
        #bill = Block()
        name = newIdent(0)
        t = time.time()
        s = t+1
        diff = 1.0
        params = {"ident":name, "disco":t, "arriv":s, "parent":None, "diff":diff}
        bill = Block(params)
        self.assertEqual(bill.ident,name)
        self.assertEqual(bill.discoTimestamp,t)
        self.assertEqual(bill.arrivTimestamp,t+1)
        self.assertTrue(bill.parent is None)
        self.assertEqual(bill.diff,diff)
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_Block)
unittest.TextTestRunner(verbosity=1).run(suite)
