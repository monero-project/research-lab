# Test suite for Dumb25519 and friends

from dumb25519 import *
import ecies
import stealth
import account
import unittest
import polycom

class TestDumb25519(unittest.TestCase):
    def test_point_operations(self):
        # test point addition and subtraction
        self.assertEqual(Z+Z,Z)
        self.assertEqual(G+Z,G)
        self.assertEqual(Z+G,G)
        self.assertEqual(G-G,Z)

        # test curve membership
        self.assertFalse(Point(0,0).on_curve())
        self.assertTrue(G.on_curve())
        self.assertTrue(Z.on_curve())
    
    def test_scalar_operations(self):
        # test basic scalar operations
        self.assertEqual(Scalar(0),Scalar(l))
        self.assertEqual(Scalar(0)+Scalar(1),Scalar(1))
        self.assertEqual(Scalar(0)-Scalar(1),Scalar(-1))
        self.assertEqual(Scalar(1)*Scalar(1),Scalar(1))
        self.assertEqual(Scalar(2)/Scalar(2),Scalar(1))
        self.assertEqual(Scalar(3)/Scalar(2),Scalar(1))
        self.assertEqual(Scalar(0)/Scalar(2),Scalar(0))
        self.assertEqual(Scalar(2)**0,Scalar(1))
        self.assertEqual(Scalar(2)**1,Scalar(2))
        self.assertEqual(Scalar(2)**2,Scalar(4))
        self.assertEqual(Scalar(2)**3,Scalar(8))
        self.assertEqual(Scalar(1)**0,Scalar(1))
        self.assertEqual(Scalar(1)**1,Scalar(1))
        self.assertEqual(Scalar(1)**2,Scalar(1))
        self.assertEqual(Scalar(0)**1,Scalar(0))
        self.assertEqual(Scalar(0)**2,Scalar(0))

        # test scalar inversion
        self.assertEqual(Scalar(1).invert(),Scalar(1))
        with self.assertRaises(ZeroDivisionError):
            Scalar(0).invert()
        self.assertEqual(Scalar(2)*Scalar(2).invert(),Scalar(1))

        # test scalar inequality
        self.assertTrue(Scalar(1) > 0)
        self.assertFalse(Scalar(1) < 0)
        self.assertFalse(Scalar(0) > 0)
        self.assertFalse(Scalar(0) < 0)

    def test_mixed_operations(self):
        # test mixed-type operations
        self.assertEqual(G*Scalar(0),Z)
        self.assertEqual(G*Scalar(1),G)
        self.assertEqual(G*Scalar(2),G+G)
        self.assertEqual(G+G*Scalar(-1),Z)
        self.assertEqual(G-G*Scalar(-1),G+G)

        # test bad types in mixed operations
        with self.assertRaises(TypeError):
            G+Scalar(1)
        with self.assertRaises(TypeError):
            G-Scalar(1)
        with self.assertRaises(TypeError):
            G*Z
        with self.assertRaises(TypeError):
            Scalar(1)+G
        with self.assertRaises(TypeError):
            Scalar(1)-G
        with self.assertRaises(TypeError):
            Scalar(1)*G
        with self.assertRaises(TypeError):
            Scalar(1)/G
        with self.assertRaises(TypeError):
            G == Scalar(1)
        with self.assertRaises(TypeError):
            Scalar(1) == G

    def test_hashing(self):
        # test hashing strings
        hash_to_point('The Human Fund: Money For People')
        hash_to_scalar('The Human Fund: Money For People')
        hash_to_point(str(G))
        hash_to_scalar(str(G))
        hash_to_point(str(8675309))
        hash_to_scalar(str(8675309))

        # test hashing non-string types
        with self.assertRaises(TypeError):
            hash_to_point(8675309)
        with self.assertRaises(TypeError):
            hash_to_scalar(8675309)
        with self.assertRaises(TypeError):
            hash_to_point(G)
        with self.assertRaises(TypeError):
            hash_to_scalar(G)

    def test_random(self):
        random_scalar()
        random_point()

    def test_flatten(self):
        # ensure that nested lists are flattened
        L = [0,[[1],2,3],[4,5,6],[[[7,8],9],10,11],12]
        self.assertEqual(flatten(L),range(13))

    def test_pedersen(self):
        r = random_scalar()
        self.assertEqual(pedersen_commit([Scalar(0)],r),H*r) # G*0 + H*r = H*r
        self.assertEqual(pedersen_commit([r],Scalar(0)),hash_to_point('dumb25519 Gi'+str(0))*r) # G_0*r + H*0 = G_0*r

class TestECIES(unittest.TestCase):
    def test_decrypt(self):
        # generate an ECIES key pair
        skey = ecies.gen_private_key()
        pkey = ecies.gen_public_key(skey)
        tag = random_scalar()
        
        # test decryption
        self.assertEqual(ecies.decrypt(skey,tag,ecies.encrypt(pkey,tag,'')),'')
        self.assertEqual(ecies.decrypt(skey,tag,ecies.encrypt(pkey,tag,'message')),'message')
        self.assertEqual(ecies.decrypt(skey,tag,ecies.encrypt(pkey,tag,'Four score and seven long messages ago')),'Four score and seven long messages ago')
        self.assertEqual(ecies.decrypt(skey,tag,ecies.encrypt(pkey,tag,str(G))),str(G))

        # test bad types
        with self.assertRaises(TypeError):
            ecies.decrypt(None,tag,ecies.encrypt(None,tag,''))
        with self.assertRaises(TypeError):
            ecies.decrypt(skey,tag,None)

class TestStealthAccount(unittest.TestCase):
    def test_gen_account(self):
        # generate a stealth account
        stealth_private_key = stealth.gen_private_key()
        stealth_public_key = stealth.gen_public_key(stealth_private_key)

        # ensure all properties are set
        self.assertIsNotNone(stealth_private_key.tsk)
        self.assertIsNotNone(stealth_private_key.ssk)
        self.assertIsNotNone(stealth_private_key.x)

        self.assertIsNotNone(stealth_public_key.tpk)
        self.assertIsNotNone(stealth_public_key.spk)
        self.assertIsNotNone(stealth_public_key.X)

class TestAccount(unittest.TestCase):
    def test_gen_account(self):
        # generate a stealth account
        stealth_private_key = stealth.gen_private_key()
        stealth_public_key = stealth.gen_public_key(stealth_private_key)

        # generate a one-time account and deposit key
        a = random_scalar()
        ot_account,deposit_key = account.gen_account(stealth_public_key,a)

        # ensure all properties are set
        self.assertIsNotNone(ot_account.pk)
        self.assertIsNotNone(ot_account.co)
        self.assertIsNotNone(ot_account._ek)
        self.assertIsNotNone(ot_account._a)
        self.assertIsNotNone(ot_account._r)
        self.assertIsNotNone(deposit_key.a)
        self.assertIsNotNone(deposit_key.r)

    def test_receive(self):
        # generate a stealth account and a second stealth private key
        stealth_private_key = stealth.gen_private_key()
        stealth_public_key = stealth.gen_public_key(stealth_private_key)
        bad_private_key = stealth.gen_private_key()

        # generate a one-time account and deposit key
        a = random_scalar()
        ot_account,deposit_key = account.gen_account(stealth_public_key,a)

        # we cannot receive someone else's one-time account
        with self.assertRaises(Exception):
            account.receive(bad_private_key,ot_account)

        # we can receive our own one-time account
        account.receive(stealth_private_key,ot_account)

    def test_nary(self):
        # test for bad types in n-ary decompositions (they require integers)
        with self.assertRaises(ArithmeticError):
            account.nary(None,2)
        with self.assertRaises(ArithmeticError):
            account.nary(1,None)
        with self.assertRaises(ArithmeticError):
            account.nary(0,0)
        with self.assertRaises(ArithmeticError):
            account.nary(-1,2)
        with self.assertRaises(IndexError):
            account.nary(2,2,0)

        # test decompositions with and without padding
        self.assertEqual(account.nary(0,2),[0])
        self.assertEqual(account.nary(0,2,2),[0,0])
        self.assertEqual(account.nary(1,2),[1])
        self.assertEqual(account.nary(1,3),[1])
        self.assertEqual(account.nary(8,3),[2,2])
        self.assertEqual(account.nary(27,3),[0,0,0,1])
        self.assertEqual(account.nary(27,3,3),[0,0,0,1])
        self.assertEqual(account.nary(27,3,4),[0,0,0,1])
        self.assertEqual(account.nary(27,3,5),[0,0,0,1,0])
        self.assertEqual(account.nary(26,3,5),[2,2,2,0,0])

    def test_1_1_spend(self): # 1 in, 1 out
        # generate a sender and recipient stealth account
        sender_private_key = stealth.gen_private_key()
        sender_public_key = stealth.gen_public_key(sender_private_key)
        recipient_private_key = stealth.gen_private_key()
        recipient_public_key = stealth.gen_public_key(recipient_private_key)

        # generate a ring of one-time accounts addressed to unknown recipients
        accounts_ring = []
        for i in range(account.R - 1): 
            temp_private_key = stealth.gen_private_key()
            temp_public_key = stealth.gen_public_key(temp_private_key)
            temp_ot_account,temp_deposit_key = account.gen_account(temp_public_key,random_scalar())
            accounts_ring.append(temp_ot_account)

        # generate a one-time account addressed to the sender and receive it
        ot_sender,deposit_sender = account.gen_account(sender_public_key,random_scalar())
        withdrawal_key = account.receive(sender_private_key,ot_sender)

        # generate a one-time account addressed to the recipient
        ot_recipient,deposit_recipient = account.gen_account(recipient_public_key,random_scalar())

        # spend the input
        tx = account.Transaction([withdrawal_key.tag],accounts_ring,[ot_recipient])
        account.spend([withdrawal_key],[deposit_recipient],tx,'spend memo')

class TestPolyCom(unittest.TestCase):
    def test_m_n_d_1_1_0_steps(self):
        m = 1
        n = 1
        d = 0

        h = [random_scalar() for i in range(m*n+d+1)]

        # test matrix construction
        msg1,state = polycom.commit(h,m,n,d)
        M = state[0]
        b = state[1]
        self.assertEqual(M,[[h[0]-b[0],Scalar(0)],[b[0],h[1]]])

        # test evaluation commitments
        x = random_scalar()
        msg2 = polycom.evaluate(state,x)
        hbar = msg2[0]
        self.assertEqual(hbar[0],h[0]-b[0])
        self.assertEqual(hbar[1],b[0]+h[1]*x)

    def test_matrix_sizes(self):
        for n in [1,2]:
            for m in [1,2]:
                for d in range(m):
                    h = []
                    for i in range(m*n+d+1):
                        h.append(random_scalar())

                    # run the proof
                    msg1,state = polycom.commit(h,m,n,d)
                    x = random_scalar()
                    msg2 = polycom.evaluate(state,x)

                    # verify and check for valid evaluation
                    result = Scalar(0)
                    for j in range(m*n+d+1):
                        result += h[j]*(x**j)
                    self.assertEqual(polycom.verify(msg1,msg2,x,m,n,d),result)

for test in [TestDumb25519,TestECIES,TestStealthAccount,TestAccount,TestPolyCom]:
    unittest.TextTestRunner(verbosity=2,failfast=True).run(unittest.TestLoader().loadTestsFromTestCase(test))
