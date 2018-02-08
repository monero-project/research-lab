// NOTE: this interchanges the roles of G and H to match other code's behavior

package how.monero.hodl.bulletproof;

import how.monero.hodl.crypto.Curve25519Point;
import how.monero.hodl.crypto.Scalar;
import how.monero.hodl.crypto.CryptoUtil;
import how.monero.hodl.util.ByteUtil;
import java.math.BigInteger;
import how.monero.hodl.util.VarInt;
import java.util.Random;

import static how.monero.hodl.crypto.Scalar.randomScalar;
import static how.monero.hodl.crypto.CryptoUtil.*;
import static how.monero.hodl.util.ByteUtil.*;

public class LinearBulletproof
{
    private static int N;
    private static Curve25519Point G;
    private static Curve25519Point H;
    private static Curve25519Point[] Gi;
    private static Curve25519Point[] Hi;

    public static class ProofTuple
    {
        private Curve25519Point V;
        private Curve25519Point A;
        private Curve25519Point S;
        private Curve25519Point T1;
        private Curve25519Point T2;
        private Scalar taux;
        private Scalar mu;
        private Scalar[] l;
        private Scalar[] r;

        public ProofTuple(Curve25519Point V, Curve25519Point A, Curve25519Point S, Curve25519Point T1, Curve25519Point T2, Scalar taux, Scalar mu, Scalar[] l, Scalar[] r)
        {
            this.V = V;
            this.A = A;
            this.S = S;
            this.T1 = T1;
            this.T2 = T2;
            this.taux = taux;
            this.mu = mu;
            this.l = l;
            this.r = r;
        }
    }

    /* Given two scalar arrays, construct a vector commitment */
    public static Curve25519Point VectorExponent(Scalar[] a, Scalar[] b)
    {
        Curve25519Point Result = Curve25519Point.ZERO;
        for (int i = 0; i < N; i++)
        {
            Result = Result.add(Gi[i].scalarMultiply(a[i]));
            Result = Result.add(Hi[i].scalarMultiply(b[i]));
        }
        return Result;
    }

    /* Given a scalar, construct a vector of powers */
    public static Scalar[] VectorPowers(Scalar x)
    {
        Scalar[] result = new Scalar[N];
        for (int i = 0; i < N; i++)
        {
            result[i] = x.pow(i);
        }
        return result;
    }

    /* Given two scalar arrays, construct the inner product */
    public static Scalar InnerProduct(Scalar[] a, Scalar[] b)
    {
        Scalar result = Scalar.ZERO;
        for (int i = 0; i < N; i++)
        {
            result = result.add(a[i].mul(b[i]));
        }
        return result;
    }

    /* Given two scalar arrays, construct the Hadamard product */
    public static Scalar[] Hadamard(Scalar[] a, Scalar[] b)
    {
        Scalar[] result = new Scalar[N];
        for (int i = 0; i < N; i++)
        {
            result[i] = a[i].mul(b[i]);
        }
        return result;
    }

    /* Add two vectors */
    public static Scalar[] VectorAdd(Scalar[] a, Scalar[] b)
    {
        Scalar[] result = new Scalar[N];
        for (int i = 0; i < N; i++)
        {
            result[i] = a[i].add(b[i]);
        }
        return result;
    }

    /* Subtract two vectors */
    public static Scalar[] VectorSubtract(Scalar[] a, Scalar[] b)
    {
        Scalar[] result = new Scalar[N];
        for (int i = 0; i < N; i++)
        {
            result[i] = a[i].sub(b[i]);
        }
        return result;
    }

    /* Multiply a scalar and a vector */
    public static Scalar[] VectorScalar(Scalar[] a, Scalar x)
    {
        Scalar[] result = new Scalar[N];
        for (int i = 0; i < N; i++)
        {
            result[i] = a[i].mul(x);
        }
        return result;
    }

    /* Compute the inverse of a scalar, the stupid way */
    public static Scalar Invert(Scalar x)
    {
        Scalar inverse = new Scalar(x.toBigInteger().modInverse(CryptoUtil.l));
        assert x.mul(inverse).equals(Scalar.ONE);

        return inverse;
    }

    /* Compute the value of k(y,z) */
    public static Scalar ComputeK(Scalar y, Scalar z)
    {
        Scalar result = Scalar.ZERO;
        result = result.sub(z.sq().mul(InnerProduct(VectorPowers(Scalar.ONE),VectorPowers(y))));
        result = result.sub(z.pow(3).mul(InnerProduct(VectorPowers(Scalar.ONE),VectorPowers(Scalar.TWO))));

        return result;
    }

    /* Given a value v (0..2^N-1) and a mask gamma, construct a range proof */
    public static ProofTuple PROVE(Scalar v, Scalar gamma)
    {
        Curve25519Point V = H.scalarMultiply(v).add(G.scalarMultiply(gamma));

        // This hash is updated for Fiat-Shamir throughout the proof
        Scalar hashCache = hashToScalar(V.toBytes());
        
        // PAPER LINES 36-37
        Scalar[] aL = new Scalar[N];
        Scalar[] aR = new Scalar[N];

        BigInteger tempV = v.toBigInteger();
        for (int i = N-1; i >= 0; i--)
        {
            BigInteger basePow = BigInteger.valueOf(2).pow(i);
            if (tempV.divide(basePow).equals(BigInteger.ZERO))
            {
                aL[i] = Scalar.ZERO;
            }
            else
            {
                aL[i] = Scalar.ONE;
                tempV = tempV.subtract(basePow);
            }

            aR[i] = aL[i].sub(Scalar.ONE);
        }

        // DEBUG: Test to ensure this recovers the value
        BigInteger test_aL = BigInteger.ZERO;
        BigInteger test_aR = BigInteger.ZERO;
        for (int i = 0; i < N; i++)
        {
            if (aL[i].equals(Scalar.ONE))
                test_aL = test_aL.add(BigInteger.valueOf(2).pow(i));
            if (aR[i].equals(Scalar.ZERO))
                test_aR = test_aR.add(BigInteger.valueOf(2).pow(i));
        }
        assert test_aL.equals(v.toBigInteger());
        assert test_aR.equals(v.toBigInteger());

        // PAPER LINES 38-39
        Scalar alpha = randomScalar();
        Curve25519Point A = VectorExponent(aL,aR).add(G.scalarMultiply(alpha));

        // PAPER LINES 40-42
        Scalar[] sL = new Scalar[N];
        Scalar[] sR = new Scalar[N];
        for (int i = 0; i < N; i++)
        {
            sL[i] = randomScalar();
            sR[i] = randomScalar();
        }
        Scalar rho = randomScalar();
        Curve25519Point S = VectorExponent(sL,sR).add(G.scalarMultiply(rho));

        // PAPER LINES 43-45
        hashCache = hashToScalar(concat(hashCache.bytes,A.toBytes()));
        hashCache = hashToScalar(concat(hashCache.bytes,S.toBytes()));
        Scalar y = hashCache;
        hashCache = hashToScalar(hashCache.bytes);
        Scalar z = hashCache;

        Scalar t0 = Scalar.ZERO;
        Scalar t1 = Scalar.ZERO;
        Scalar t2 = Scalar.ZERO;
        
        t0 = t0.add(z.mul(InnerProduct(VectorPowers(Scalar.ONE),VectorPowers(y))));
        t0 = t0.add(z.sq().mul(v));
        Scalar k = ComputeK(y,z);
        t0 = t0.add(k);

        // DEBUG: Test the value of t0 has the correct form
        Scalar test_t0 = Scalar.ZERO;
        test_t0 = test_t0.add(InnerProduct(aL,Hadamard(aR,VectorPowers(y))));
        test_t0 = test_t0.add(z.mul(InnerProduct(VectorSubtract(aL,aR),VectorPowers(y))));
        test_t0 = test_t0.add(z.sq().mul(InnerProduct(VectorPowers(Scalar.TWO),aL)));
        test_t0 = test_t0.add(k);
        assert test_t0.equals(t0);

        t1 = t1.add(InnerProduct(VectorSubtract(aL,VectorScalar(VectorPowers(Scalar.ONE),z)),Hadamard(VectorPowers(y),sR)));
        t1 = t1.add(InnerProduct(sL,VectorAdd(Hadamard(VectorPowers(y),VectorAdd(aR,VectorScalar(VectorPowers(Scalar.ONE),z))),VectorScalar(VectorPowers(Scalar.TWO),z.sq()))));
        t2 = t2.add(InnerProduct(sL,Hadamard(VectorPowers(y),sR)));

        // PAPER LINES 47-48
        Scalar tau1 = randomScalar();
        Scalar tau2 = randomScalar();
        Curve25519Point T1 = H.scalarMultiply(t1).add(G.scalarMultiply(tau1));
        Curve25519Point T2 = H.scalarMultiply(t2).add(G.scalarMultiply(tau2));

        // PAPER LINES 49-51
        hashCache = hashToScalar(concat(hashCache.bytes,z.bytes));
        hashCache = hashToScalar(concat(hashCache.bytes,T1.toBytes()));
        hashCache = hashToScalar(concat(hashCache.bytes,T2.toBytes()));
        Scalar x = hashCache;
        
        // PAPER LINES 52-53
        Scalar taux = Scalar.ZERO;
        taux = tau1.mul(x);
        taux = taux.add(tau2.mul(x.sq()));
        taux = taux.add(gamma.mul(z.sq()));
        Scalar mu = x.mul(rho).add(alpha);

        // PAPER LINES 54-57
        Scalar[] l = new Scalar[N];
        Scalar[] r = new Scalar[N];

        l = VectorAdd(VectorSubtract(aL,VectorScalar(VectorPowers(Scalar.ONE),z)),VectorScalar(sL,x));
        r = VectorAdd(Hadamard(VectorPowers(y),VectorAdd(aR,VectorAdd(VectorScalar(VectorPowers(Scalar.ONE),z),VectorScalar(sR,x)))),VectorScalar(VectorPowers(Scalar.TWO),z.sq()));

        // DEBUG: Test if the l and r vectors match the polynomial forms
        Scalar test_t = Scalar.ZERO;
        test_t = test_t.add(t0).add(t1.mul(x));
        test_t = test_t.add(t2.mul(x.sq()));
        assert test_t.equals(InnerProduct(l,r));

        // PAPER LINE 58
        return new ProofTuple(V,A,S,T1,T2,taux,mu,l,r);
    }

    /* Given a range proof, determine if it is valid */
    public static boolean VERIFY(ProofTuple proof)
    {
        // Reconstruct the challenges
        Scalar hashCache = hashToScalar(proof.V.toBytes());
        hashCache = hashToScalar(concat(hashCache.bytes,proof.A.toBytes()));
        hashCache = hashToScalar(concat(hashCache.bytes,proof.S.toBytes()));
        Scalar y = hashCache;
        hashCache = hashToScalar(hashCache.bytes);
        Scalar z = hashCache;
        hashCache = hashToScalar(concat(hashCache.bytes,z.bytes));
        hashCache = hashToScalar(concat(hashCache.bytes,proof.T1.toBytes()));
        hashCache = hashToScalar(concat(hashCache.bytes,proof.T2.toBytes()));
        Scalar x = hashCache;

        // PAPER LINE 60
        Scalar t = InnerProduct(proof.l,proof.r);

        // PAPER LINE 61
        Curve25519Point L61Left = G.scalarMultiply(proof.taux).add(H.scalarMultiply(t));

        Scalar k = ComputeK(y,z);

        Curve25519Point L61Right = H.scalarMultiply(k.add(z.mul(InnerProduct(VectorPowers(Scalar.ONE),VectorPowers(y)))));
        L61Right = L61Right.add(proof.V.scalarMultiply(z.sq()));
        L61Right = L61Right.add(proof.T1.scalarMultiply(x));
        L61Right = L61Right.add(proof.T2.scalarMultiply(x.sq()));

        if (!L61Right.equals(L61Left))
        {
            return false;
        }

        // PAPER LINE 62
        Curve25519Point P = Curve25519Point.ZERO;
        P = P.add(proof.A);
        P = P.add(proof.S.scalarMultiply(x));
        
        Scalar[] Gexp = new Scalar[N];
        for (int i = 0; i < N; i++)
            Gexp[i] = Scalar.ZERO.sub(z);

        Scalar[] Hexp = new Scalar[N];
        for (int i = 0; i < N; i++)
        {
            Hexp[i] = Scalar.ZERO;
            Hexp[i] = Hexp[i].add(z.mul(y.pow(i)));
            Hexp[i] = Hexp[i].add(z.sq().mul(Scalar.TWO.pow(i)));
            Hexp[i] = Hexp[i].mul(Invert(y).pow(i));
        }
        P = P.add(VectorExponent(Gexp,Hexp));

        // PAPER LINE 63
        for (int i = 0; i < N; i++)
        {
            Hexp[i] = Scalar.ZERO;
            Hexp[i] = Hexp[i].add(proof.r[i]);
            Hexp[i] = Hexp[i].mul(Invert(y).pow(i));
        }
        Curve25519Point L63Right = VectorExponent(proof.l,Hexp).add(G.scalarMultiply(proof.mu));

        if (!L63Right.equals(P))
        {
            return false;
        }

        return true;
    }

    public static void main(String[] args)
    {
        // Number of bits in the range
        N = 64;

        // Set the curve base points
        G = Curve25519Point.G;
        H = Curve25519Point.hashToPoint(G);
        Gi = new Curve25519Point[N];
        Hi = new Curve25519Point[N];
        for (int i = 0; i < N; i++)
        {
            Gi[i] = getHpnGLookup(2*i);
            Hi[i] = getHpnGLookup(2*i+1);
        }

        // Run a bunch of randomized trials
        Random rando = new Random();
        int TRIALS = 250;
        int count = 0;

        while (count < TRIALS)
        {
            long amount = rando.nextLong();
            if (amount > Math.pow(2,N)-1 || amount < 0)
                continue;

            ProofTuple proof = PROVE(new Scalar(BigInteger.valueOf(amount)),randomScalar());
            if (!VERIFY(proof))
                System.out.println("Test failed");

            count += 1;
        }
    }
}
