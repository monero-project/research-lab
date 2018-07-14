# Test suite for Dumb25519 and friends

from dumb25519 import *
import ecies
import unittest

class TestDumb25519(unittest.TestCase):
    def test_point_operations(self):
        self.assertEqual(Z+Z,Z)
        self.assertEqual(G+Z,G)
        self.assertEqual(Z+G,G)
        self.assertEqual(G-G,Z)
        self.assertFalse(Point(0,0).on_curve())
        self.assertTrue(G.on_curve())
        self.assertTrue(Z.on_curve())
    
    def test_scalar_operations(self):
        self.assertEqual(Scalar(0),Scalar(l))
        self.assertEqual(Scalar(0)+Scalar(1),Scalar(1))
        self.assertEqual(Scalar(0)-Scalar(1),Scalar(-1))
        self.assertEqual(Scalar(1)*Scalar(1),Scalar(1))
        self.assertEqual(Scalar(2)/Scalar(2),Scalar(1))
        self.assertEqual(Scalar(3)/Scalar(2),Scalar(1))
        self.assertEqual(Scalar(0)/Scalar(2),Scalar(0))

    def test_mixed_operations(self):
        self.assertEqual(G*Scalar(0),Z)
        self.assertEqual(G*Scalar(1),G)
        self.assertEqual(G*Scalar(2),G+G)
        self.assertEqual(G+G*Scalar(-1),Z)
        self.assertEqual(G-G*Scalar(-1),G+G)

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
        hash_to_point('The Human Fund: Money For People')
        hash_to_scalar('The Human Fund: Money For People')
        with self.assertRaises(TypeError):
            hash_to_point(8675309)
        hash_to_point(str(8675309))
        with self.assertRaises(TypeError):
            hash_to_scalar(8675309)
        hash_to_scalar(str(8675309))
        with self.assertRaises(TypeError):
            hash_to_point(G)
        hash_to_point(str(G))
        with self.assertRaises(TypeError):
            hash_to_scalar(G)
        hash_to_scalar(str(G))

    def test_random(self):
        random_scalar()
        random_point()

class TestECIES(unittest.TestCase):
    def test_decrypt(self):
        skey = random_scalar()
        pkey = G*skey
        tag = random_scalar()
        
        self.assertEqual(ecies.decrypt(skey,tag,ecies.encrypt(pkey,tag,'')),'')
        self.assertEqual(ecies.decrypt(skey,tag,ecies.encrypt(pkey,tag,'message')),'message')
        self.assertEqual(ecies.decrypt(skey,tag,ecies.encrypt(pkey,tag,'Four score and seven long messages ago')),'Four score and seven long messages ago')
        self.assertEqual(ecies.decrypt(skey,tag,ecies.encrypt(pkey,tag,str(G))),str(G))

        with self.assertRaises(TypeError):
            ecies.decrypt(None,tag,ecies.encrypt(None,tag,''))
        with self.assertRaises(TypeError):
            ecies.decrypt(skey,tag,None)

unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromTestCase(TestDumb25519))
unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromTestCase(TestECIES))
