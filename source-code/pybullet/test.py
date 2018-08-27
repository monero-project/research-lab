# Test suite for pybullet

import dumb25519
from dumb25519 import Z, G, H, Point, Scalar, PointVector, ScalarVector, random_point, random_scalar, hash_to_scalar, hash_to_point
import pybullet
import random
import unittest

class TestDumb25519(unittest.TestCase):
    def test_point_ops(self):
        self.assertEqual(Z+Z,Z)
        self.assertEqual(G+Z,G)
        self.assertEqual(Z+G,G)
        self.assertEqual(G-G,Z)

        self.assertFalse(Point(0,0).on_curve())
        self.assertTrue(G.on_curve())
        self.assertTrue(Z.on_curve())

    def test_scalar_ops(self):
        self.assertEqual(Scalar(0),Scalar(dumb25519.l))
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

        self.assertEqual(Scalar(1).invert(),Scalar(1))
        with self.assertRaises(ZeroDivisionError):
            Scalar(0).invert()
        self.assertEqual(Scalar(2)*Scalar(2).invert(),Scalar(1))

        self.assertTrue(Scalar(1) > 0)
        self.assertFalse(Scalar(1) < 0)
        self.assertFalse(Scalar(0) > 0)
        self.assertFalse(Scalar(0) < 0)

        self.assertTrue(Scalar(3) % Scalar(2),Scalar(1))
        self.assertTrue(Scalar(2) % Scalar(2),Scalar(0))

    def test_mixed_ops(self):
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
        hash_to_point(str(G))
        hash_to_scalar(str(G))
        hash_to_point(str(8675309))
        hash_to_scalar(str(8675309))

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
        L = [0,[[1],2,3],[4,5,6],[[[7,8],9],10,11],12]
        self.assertEqual(dumb25519.flatten(L),range(13))

class TestMultiexp(unittest.TestCase):
    def test_0(self):
        self.assertEqual(dumb25519.multiexp([]),Z)

    def test_1_G_0(self):
        data = [[G,Scalar(0)]]
        self.assertEqual(dumb25519.multiexp(data),Z)

    def test_1_G_1(self):
        data = [[G,Scalar(1)]]
        self.assertEqual(dumb25519.multiexp(data),G)

    def test_1_G_2(self):
        data = [[G,Scalar(2)]]
        self.assertEqual(dumb25519.multiexp(data),G*Scalar(2))

    def test_2_G_1_H_2(self):
        data = [[G,Scalar(1)],[H,Scalar(2)]]
        self.assertEqual(dumb25519.multiexp(data),G+H*Scalar(2))

    def test_2_G_2_G_n1(self):
        data = [[G,Scalar(2)],[G,Scalar(-1)]]
        self.assertEqual(dumb25519.multiexp(data),G)

    def test_8_random(self):
        data = [[random_point(),random_scalar()] for i in range(8)]
        result = Z
        for datum in data:
            result += datum[0]*datum[1]
        self.assertEqual(dumb25519.multiexp(data),result)

class TestVectorOps(unittest.TestCase):
    def test_point_vector_add(self):
        l = 3
        V = PointVector([random_point() for i in range(l)])
        W = PointVector([random_point() for i in range(l)])
        X = V+W

        self.assertEqual(len(X),l)
        for i in range(l):
            self.assertEqual(X[i],V[i]+W[i])

    def test_point_vector_sub(self):
        l = 3
        V = PointVector([random_point() for i in range(l)])
        W = PointVector([random_point() for i in range(l)])
        X = V-W

        self.assertEqual(len(X),l)
        for i in range(l):
            self.assertEqual(X[i],V[i]-W[i])

    def test_point_vector_mul_scalar(self):
        l = 3
        V = PointVector([random_point() for i in range(l)])
        s = random_scalar()
        W = V*s

        self.assertEqual(len(W),l)
        for i in range(l):
            self.assertEqual(W[i],V[i]*s)

    def test_point_vector_mul_scalar_vector(self):
        l = 3
        V = PointVector([random_point() for i in range(l)])
        v = ScalarVector([random_scalar() for i in range(l)])
        W = V*v

        R = dumb25519.Z
        for i in range(l):
            R += V[i]*v[i]
        self.assertEqual(W,R)

    def test_point_vector_hadamard(self):
        l = 3
        V = PointVector([random_point() for i in range(l)])
        W = PointVector([random_point() for i in range(l)])
        X = V*W

        self.assertEqual(len(X),l)
        for i in range(l):
            self.assertEqual(X[i],V[i]+W[i])

    def test_point_vector_extend(self):
        l = 3
        points = [random_point() for i in range(2*l)]
        V = PointVector(points[:l])
        W = PointVector(points[l:])
        V.extend(W)

        T = PointVector(points)
        self.assertEqual(len(V),len(T))
        self.assertEqual(V.points,T.points)

    def test_point_vector_slice(self):
        l = 3
        points = [random_point() for i in range(2*l)]
        V = PointVector(points)
        W = V[:l]

        self.assertEqual(len(W),l)
        self.assertEqual(W.points,points[:l])

    def test_scalar_vector_add(self):
        l = 3
        v = ScalarVector([random_scalar() for i in range(l)])
        w = ScalarVector([random_scalar() for i in range(l)])
        x = v+w

        self.assertEqual(len(x),l)
        for i in range(l):
            self.assertEqual(x[i],v[i]+w[i])

    def test_scalar_vector_sub(self):
        l = 3
        v = ScalarVector([random_scalar() for i in range(l)])
        w = ScalarVector([random_scalar() for i in range(l)])
        x = v-w

        self.assertEqual(len(x),l)
        for i in range(l):
            self.assertEqual(x[i],v[i]-w[i])

    def test_scalar_vector_mul_scalar(self):
        l = 3
        v = ScalarVector([random_scalar() for i in range(l)])
        s = random_scalar()
        w = v*s

        self.assertEqual(len(w),l)
        for i in range(l):
            self.assertEqual(w[i],v[i]*s)

    def test_scalar_vector_hadamard(self):
        l = 3
        v = ScalarVector([random_scalar() for i in range(l)])
        w = ScalarVector([random_scalar() for i in range(l)])
        x = v*w

        self.assertEqual(len(x),l)
        for i in range(l):
            self.assertEqual(x[i],v[i]*w[i])

    def test_inner_product(self):
        l = 3
        v = ScalarVector([random_scalar() for i in range(l)])
        w = ScalarVector([random_scalar() for i in range(l)])
        x = v**w

        r = Scalar(0)
        for i in range(l):
            r += v[i]*w[i]
        self.assertEqual(r,x)

    def test_scalar_vector_extend(self):
        v = ScalarVector([Scalar(0),Scalar(1)])
        w = ScalarVector([Scalar(2),Scalar(3)])
        v.extend(w)

        t = ScalarVector([Scalar(0),Scalar(1),Scalar(2),Scalar(3)])
        self.assertEqual(len(v),len(t))
        self.assertEqual(v.scalars,t.scalars)

    def test_scalar_vector_slice(self):
        l = 3
        scalars = [random_scalar() for i in range(2*l)]
        v = ScalarVector(scalars)
        w = v[:l]

        self.assertEqual(len(w),l)
        self.assertEqual(w.scalars,scalars[:l])

    def test_batch_inversion(self):
        l = 8
        v = ScalarVector([random_scalar() for i in range(l)])
        v.append(Scalar(1))
        v.append(Scalar(dumb25519.l-1))
        w = v.invert()

        for i in range(len(v)):
            self.assertEqual(v[i]*w[i],Scalar(1))

    def test_bad_batch_inversion(self):
        with self.assertRaises(ArithmeticError):
            ScalarVector([Scalar(1),Scalar(0)]).invert()

class TestBulletOps(unittest.TestCase):
    def test_scalar_to_bits(self):
        N = 8
        scalars = [Scalar(0),Scalar(1),Scalar(2),Scalar(2**(N-1)),Scalar(2**N-1)]
        for scalar in scalars:
            bits = pybullet.scalar_to_bits(scalar,N) # break into bits

            # now reassemble the original scalar
            result = Scalar(0)
            for i,bit in enumerate(bits):
                result += bit*Scalar(2**i)
            self.assertEqual(result,scalar)

            self.assertEqual(len(bits),N)

    def test_sum_scalar(self):
        s = Scalar(2)
        l = 4
        self.assertEqual(pybullet.sum_scalar(s,l),Scalar(15))

class TestBullet(unittest.TestCase):
    def test_prove_verify_m_1_n_4(self):
        M = 1
        N = 4
        data = [[Scalar(random.randint(0,2**N-1)),random_scalar()] for i in range(M)]
        pybullet.verify([pybullet.prove(data,N)],N)

    def test_prove_verify_m_2_n_4(self):
        M = 2
        N = 4
        data = [[Scalar(random.randint(0,2**N-1)),random_scalar()] for i in range(M)]
        pybullet.verify([pybullet.prove(data,N)],N)

    def test_invalid_value(self):
        M = 1
        N = 4
        data = [[Scalar(random.randint(2**N,2**(N+1)-1)),random_scalar()]]
        with self.assertRaises(ArithmeticError):
            pybullet.verify([pybullet.prove(data,N)],N)

    def test_batch_2_m_1_n_4(self):
        M = 1
        N = 4
        data = [[Scalar(random.randint(0,2**N-1)),random_scalar()] for i in range(M)]
        proof1 = pybullet.prove(data,N)
        data = [[Scalar(random.randint(0,2**N-1)),random_scalar()] for i in range(M)]
        proof2 = pybullet.prove(data,N)
        pybullet.verify([proof1,proof2],N)

    def test_batch_2_m_1_2_n_4(self):
        M = 1
        N = 4
        data = [[Scalar(random.randint(0,2**N-1)),random_scalar()] for i in range(M)]
        proof1 = pybullet.prove(data,N)
        M = 2
        data = [[Scalar(random.randint(0,2**N-1)),random_scalar()] for i in range(M)]
        proof2 = pybullet.prove(data,N)
        pybullet.verify([proof1,proof2],N)

    def test_invalid_batch_2_m_1_2_n_4(self):
        M = 1
        N = 4
        data = [[Scalar(random.randint(0,2**N-1)),random_scalar()] for i in range(M)]
        proof1 = pybullet.prove(data,N)
        M = 2
        data = [[Scalar(random.randint(2**N,2**(N+1)-1)),random_scalar()] for i in range(M)]
        proof2 = pybullet.prove(data,N)
        with self.assertRaises(ArithmeticError):
            pybullet.verify([proof1,proof2],N)

for test in [TestDumb25519,TestMultiexp,TestVectorOps,TestBulletOps,TestBullet]:
    unittest.TextTestRunner(verbosity=2,failfast=True).run(unittest.TestLoader().loadTestsFromTestCase(test))
