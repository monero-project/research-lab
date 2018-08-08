# Test suite for pybullet

import dumb25519
from dumb25519 import Scalar, Point
import pybullet
import random
import unittest

class TestVectorOps(unittest.TestCase):
    def test_point_vector_add(self):
        l = 3
        V = dumb25519.PointVector([dumb25519.random_point() for i in range(l)])
        W = dumb25519.PointVector([dumb25519.random_point() for i in range(l)])
        X = V+W

        self.assertEqual(len(X),l)
        for i in range(l):
            self.assertEqual(X[i],V[i]+W[i])

    def test_point_vector_sub(self):
        l = 3
        V = dumb25519.PointVector([dumb25519.random_point() for i in range(l)])
        W = dumb25519.PointVector([dumb25519.random_point() for i in range(l)])
        X = V-W

        self.assertEqual(len(X),l)
        for i in range(l):
            self.assertEqual(X[i],V[i]-W[i])

    def test_point_vector_mul_scalar(self):
        l = 3
        V = dumb25519.PointVector([dumb25519.random_point() for i in range(l)])
        s = dumb25519.random_scalar()
        W = V*s

        self.assertEqual(len(W),l)
        for i in range(l):
            self.assertEqual(W[i],V[i]*s)

    def test_point_vector_mul_scalar_vector(self):
        l = 3
        V = dumb25519.PointVector([dumb25519.random_point() for i in range(l)])
        v = dumb25519.ScalarVector([dumb25519.random_scalar() for i in range(l)])
        W = V*v

        R = dumb25519.Z
        for i in range(l):
            R += V[i]*v[i]
        self.assertEqual(W,R)

    def test_point_vector_hadamard(self):
        l = 3
        V = dumb25519.PointVector([dumb25519.random_point() for i in range(l)])
        W = dumb25519.PointVector([dumb25519.random_point() for i in range(l)])
        X = V*W

        self.assertEqual(len(X),l)
        for i in range(l):
            self.assertEqual(X[i],V[i]+W[i])

    def test_point_vector_extend(self):
        l = 3
        points = [dumb25519.random_point() for i in range(2*l)]
        V = dumb25519.PointVector(points[:l])
        W = dumb25519.PointVector(points[l:])
        V.extend(W)

        T = dumb25519.PointVector(points)
        self.assertEqual(len(V),len(T))
        self.assertEqual(V.points,T.points)

    def test_point_vector_slice(self):
        l = 3
        points = [dumb25519.random_point() for i in range(2*l)]
        V = dumb25519.PointVector(points)
        W = V[:l]

        self.assertEqual(len(W),l)
        self.assertEqual(W.points,points[:l])

    def test_scalar_vector_add(self):
        l = 3
        v = dumb25519.ScalarVector([dumb25519.random_scalar() for i in range(l)])
        w = dumb25519.ScalarVector([dumb25519.random_scalar() for i in range(l)])
        x = v+w

        self.assertEqual(len(x),l)
        for i in range(l):
            self.assertEqual(x[i],v[i]+w[i])

    def test_scalar_vector_sub(self):
        l = 3
        v = dumb25519.ScalarVector([dumb25519.random_scalar() for i in range(l)])
        w = dumb25519.ScalarVector([dumb25519.random_scalar() for i in range(l)])
        x = v-w

        self.assertEqual(len(x),l)
        for i in range(l):
            self.assertEqual(x[i],v[i]-w[i])

    def test_scalar_vector_mul_scalar(self):
        l = 3
        v = dumb25519.ScalarVector([dumb25519.random_scalar() for i in range(l)])
        s = dumb25519.random_scalar()
        w = v*s

        self.assertEqual(len(w),l)
        for i in range(l):
            self.assertEqual(w[i],v[i]*s)

    def test_scalar_vector_hadamard(self):
        l = 3
        v = dumb25519.ScalarVector([dumb25519.random_scalar() for i in range(l)])
        w = dumb25519.ScalarVector([dumb25519.random_scalar() for i in range(l)])
        x = v*w

        self.assertEqual(len(x),l)
        for i in range(l):
            self.assertEqual(x[i],v[i]*w[i])

    def test_inner_product(self):
        l = 3
        v = dumb25519.ScalarVector([dumb25519.random_scalar() for i in range(l)])
        w = dumb25519.ScalarVector([dumb25519.random_scalar() for i in range(l)])
        x = v**w

        r = Scalar(0)
        for i in range(l):
            r += v[i]*w[i]
        self.assertEqual(r,x)

    def test_scalar_vector_extend(self):
        v = dumb25519.ScalarVector([Scalar(0),Scalar(1)])
        w = dumb25519.ScalarVector([Scalar(2),Scalar(3)])
        v.extend(w)

        t = dumb25519.ScalarVector([Scalar(0),Scalar(1),Scalar(2),Scalar(3)])
        self.assertEqual(len(v),len(t))
        self.assertEqual(v.scalars,t.scalars)

    def test_scalar_vector_slice(self):
        l = 3
        scalars = [dumb25519.random_scalar() for i in range(2*l)]
        v = dumb25519.ScalarVector(scalars)
        w = v[:l]

        self.assertEqual(len(w),l)
        self.assertEqual(w.scalars,scalars[:l])


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
        data = [[Scalar(random.randint(0,2**N-1)),dumb25519.random_scalar()] for i in range(M)]
        pybullet.verify([pybullet.prove(data,N)],N)

    def test_prove_verify_m_2_n_4(self):
        M = 2
        N = 4
        data = [[Scalar(random.randint(0,2**N-1)),dumb25519.random_scalar()] for i in range(M)]
        pybullet.verify([pybullet.prove(data,N)],N)

    def test_invalid_value(self):
        M = 1
        N = 4
        data = [[Scalar(random.randint(2**N,2**(N+1)-1)),dumb25519.random_scalar()]]
        with self.assertRaises(ArithmeticError):
            pybullet.verify([pybullet.prove(data,N)],N)

    def test_batch_2_m_1_n_4(self):
        M = 1
        N = 4
        data = [[Scalar(random.randint(0,2**N-1)),dumb25519.random_scalar()] for i in range(M)]
        proof1 = pybullet.prove(data,N)
        data = [[Scalar(random.randint(0,2**N-1)),dumb25519.random_scalar()] for i in range(M)]
        proof2 = pybullet.prove(data,N)
        pybullet.verify([proof1,proof2],N)

    def test_batch_2_m_1_2_n_4(self):
        M = 1
        N = 4
        data = [[Scalar(random.randint(0,2**N-1)),dumb25519.random_scalar()] for i in range(M)]
        proof1 = pybullet.prove(data,N)
        M = 2
        data = [[Scalar(random.randint(0,2**N-1)),dumb25519.random_scalar()] for i in range(M)]
        proof2 = pybullet.prove(data,N)
        pybullet.verify([proof1,proof2],N)

    def test_invalid_batch_2_m_1_2_n_4(self):
        M = 1
        N = 4
        data = [[Scalar(random.randint(0,2**N-1)),dumb25519.random_scalar()] for i in range(M)]
        proof1 = pybullet.prove(data,N)
        M = 2
        data = [[Scalar(random.randint(2**N,2**(N+1)-1)),dumb25519.random_scalar()] for i in range(M)]
        proof2 = pybullet.prove(data,N)
        with self.assertRaises(ArithmeticError):
            pybullet.verify([proof1,proof2],N)

for test in [TestVectorOps,TestBulletOps,TestBullet]:
    unittest.TextTestRunner(verbosity=2,failfast=True).run(unittest.TestLoader().loadTestsFromTestCase(test))
