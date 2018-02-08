// NOTE: this interchanges the roles of G and H to match other code's behavior

package how.monero.hodl.bulletproof;

import how.monero.hodl.crypto.Curve25519Point;
import how.monero.hodl.crypto.Scalar;
import how.monero.hodl.crypto.CryptoUtil;
import java.math.BigInteger;
import java.util.Random;

import static how.monero.hodl.crypto.Scalar.randomScalar;
import static how.monero.hodl.crypto.CryptoUtil.*;
import static how.monero.hodl.util.ByteUtil.*;

public class LogBulletproof
{
    private static int N;
    private static int logN;
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
        private Curve25519Point[] L;
        private Curve25519Point[] R;
        private Scalar a;
        private Scalar b;
        private Scalar t;

        public ProofTuple(Curve25519Point V, Curve25519Point A, Curve25519Point S, Curve25519Point T1, Curve25519Point T2, Scalar taux, Scalar mu, Curve25519Point[] L, Curve25519Point[] R, Scalar a, Scalar b, Scalar t)
        {
            this.V = V;
            this.A = A;
            this.S = S;
            this.T1 = T1;
            this.T2 = T2;
            this.taux = taux;
            this.mu = mu;
            this.L = L;
            this.R = R;
            this.a = a;
            this.b = b;
            this.t = t;
        }
    }

    /* Given two scalar arrays, construct a vector commitment */
    public static Curve25519Point VectorExponent(Scalar[] a, Scalar[] b)
    {
        assert a.length == N && b.length == N;

        Curve25519Point Result = Curve25519Point.ZERO;
        for (int i = 0; i < N; i++)
        {
            Result = Result.add(Gi[i].scalarMultiply(a[i]));
            Result = Result.add(Hi[i].scalarMultiply(b[i]));
        }
        return Result;
    }

    /* Compute a custom vector-scalar commitment */
    public static Curve25519Point VectorExponentCustom(Curve25519Point[] A, Curve25519Point[] B, Scalar[] a, Scalar[] b)
    {
        assert a.length == A.length && b.length == B.length && a.length == b.length;

        Curve25519Point Result = Curve25519Point.ZERO;
        for (int i = 0; i < a.length; i++)
        {
            Result = Result.add(A[i].scalarMultiply(a[i]));
            Result = Result.add(B[i].scalarMultiply(b[i]));
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
        assert a.length == b.length;

        Scalar result = Scalar.ZERO;
        for (int i = 0; i < a.length; i++)
        {
            result = result.add(a[i].mul(b[i]));
        }
        return result;
    }

    /* Given two scalar arrays, construct the Hadamard product */
    public static Scalar[] Hadamard(Scalar[] a, Scalar[] b)
    {
        assert a.length == b.length;

        Scalar[] result = new Scalar[a.length];
        for (int i = 0; i < a.length; i++)
        {
            result[i] = a[i].mul(b[i]);
        }
        return result;
    }

    /* Given two curvepoint arrays, construct the Hadamard product */
    public static Curve25519Point[] Hadamard2(Curve25519Point[] A, Curve25519Point[] B)
    {
        assert A.length == B.length;

        Curve25519Point[] Result = new Curve25519Point[A.length];
        for (int i = 0; i < A.length; i++)
        {
            Result[i] = A[i].add(B[i]);
        }
        return Result;
    }

    /* Add two vectors */
    public static Scalar[] VectorAdd(Scalar[] a, Scalar[] b)
    {
        assert a.length == b.length;

        Scalar[] result = new Scalar[a.length];
        for (int i = 0; i < a.length; i++)
        {
            result[i] = a[i].add(b[i]);
        }
        return result;
    }

    /* Subtract two vectors */
    public static Scalar[] VectorSubtract(Scalar[] a, Scalar[] b)
    {
        assert a.length == b.length;

        Scalar[] result = new Scalar[a.length];
        for (int i = 0; i < a.length; i++)
        {
            result[i] = a[i].sub(b[i]);
        }
        return result;
    }

    /* Multiply a scalar and a vector */
    public static Scalar[] VectorScalar(Scalar[] a, Scalar x)
    {
        Scalar[] result = new Scalar[a.length];
        for (int i = 0; i < a.length; i++)
        {
            result[i] = a[i].mul(x);
        }
        return result;
    }

    /* Exponentiate a curve vector by a scalar */
    public static Curve25519Point[] VectorScalar2(Curve25519Point[] A, Scalar x)
    {
        Curve25519Point[] Result = new Curve25519Point[A.length];
        for (int i = 0; i < A.length; i++)
        {
            Result[i] = A[i].scalarMultiply(x);
        }
        return Result;
    }

    /* Compute the inverse of a scalar, the stupid way */
    public static Scalar Invert(Scalar x)
    {
        Scalar inverse = new Scalar(x.toBigInteger().modInverse(CryptoUtil.l));

        assert x.mul(inverse).equals(Scalar.ONE);
        return inverse;
    }

    /* Compute the slice of a curvepoint vector */
    public static Curve25519Point[] CurveSlice(Curve25519Point[] a, int start, int stop)
    {
        Curve25519Point[] Result = new Curve25519Point[stop-start];
        for (int i = start; i < stop; i++)
        {
            Result[i-start] = a[i];
        }
        return Result;
    }

    /* Compute the slice of a scalar vector */
    public static Scalar[] ScalarSlice(Scalar[] a, int start, int stop)
    {
        Scalar[] result = new Scalar[stop-start];
        for (int i = start; i < stop; i++)
        {
            result[i-start] = a[i];
        }
        return result;
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

        // Polynomial construction before PAPER LINE 46
        Scalar t0 = Scalar.ZERO;
        Scalar t1 = Scalar.ZERO;
        Scalar t2 = Scalar.ZERO;
        
        t0 = t0.add(z.mul(InnerProduct(VectorPowers(Scalar.ONE),VectorPowers(y))));
        t0 = t0.add(z.sq().mul(v));
        Scalar k = ComputeK(y,z);
        t0 = t0.add(k);

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

        Scalar t = InnerProduct(l,r);

        // PAPER LINES 32-33
        hashCache = hashToScalar(concat(hashCache.bytes,x.bytes));
        hashCache = hashToScalar(concat(hashCache.bytes,taux.bytes));
        hashCache = hashToScalar(concat(hashCache.bytes,mu.bytes));
        hashCache = hashToScalar(concat(hashCache.bytes,t.bytes));
        Scalar x_ip = hashCache;

        // These are used in the inner product rounds
        int nprime = N;
        Curve25519Point[] Gprime = new Curve25519Point[N];
        Curve25519Point[] Hprime = new Curve25519Point[N];
        Scalar[] aprime = new Scalar[N];
        Scalar[] bprime = new Scalar[N];
        for (int i = 0; i < N; i++)
        {
            Gprime[i] = Gi[i];
            Hprime[i] = Hi[i].scalarMultiply(Invert(y).pow(i));
            aprime[i] = l[i];
            bprime[i] = r[i];
        }
        Curve25519Point[] L = new Curve25519Point[logN];
        Curve25519Point[] R = new Curve25519Point[logN];
        int round = 0; // track the index based on number of rounds
        Scalar[] w = new Scalar[logN]; // this is the challenge x in the inner product protocol

        // PAPER LINE 13
        while (nprime > 1)
        {
            // PAPER LINE 15
            nprime /= 2;

            // PAPER LINES 16-17
            Scalar cL = InnerProduct(ScalarSlice(aprime,0,nprime),ScalarSlice(bprime,nprime,bprime.length));
            Scalar cR = InnerProduct(ScalarSlice(aprime,nprime,aprime.length),ScalarSlice(bprime,0,nprime));

            // PAPER LINES 18-19
            L[round] = VectorExponentCustom(CurveSlice(Gprime,nprime,Gprime.length),CurveSlice(Hprime,0,nprime),ScalarSlice(aprime,0,nprime),ScalarSlice(bprime,nprime,bprime.length)).add(H.scalarMultiply(cL.mul(x_ip)));
            R[round] = VectorExponentCustom(CurveSlice(Gprime,0,nprime),CurveSlice(Hprime,nprime,Hprime.length),ScalarSlice(aprime,nprime,aprime.length),ScalarSlice(bprime,0,nprime)).add(H.scalarMultiply(cR.mul(x_ip)));

            // PAPER LINES 21-22
            hashCache = hashToScalar(concat(hashCache.bytes,L[round].toBytes()));
            hashCache = hashToScalar(concat(hashCache.bytes,R[round].toBytes()));
            w[round] = hashCache;

            // PAPER LINES 24-25
            Gprime = Hadamard2(VectorScalar2(CurveSlice(Gprime,0,nprime),Invert(w[round])),VectorScalar2(CurveSlice(Gprime,nprime,Gprime.length),w[round]));
            Hprime = Hadamard2(VectorScalar2(CurveSlice(Hprime,0,nprime),w[round]),VectorScalar2(CurveSlice(Hprime,nprime,Hprime.length),Invert(w[round])));

            // PAPER LINES 28-29
            aprime = VectorAdd(VectorScalar(ScalarSlice(aprime,0,nprime),w[round]),VectorScalar(ScalarSlice(aprime,nprime,aprime.length),Invert(w[round])));
            bprime = VectorAdd(VectorScalar(ScalarSlice(bprime,0,nprime),Invert(w[round])),VectorScalar(ScalarSlice(bprime,nprime,bprime.length),w[round]));

            round += 1;
        }

        // PAPER LINE 58 (with inclusions from PAPER LINE 8 and PAPER LINE 20)
        return new ProofTuple(V,A,S,T1,T2,taux,mu,L,R,aprime[0],bprime[0],t);
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
        hashCache = hashToScalar(concat(hashCache.bytes,x.bytes));
        hashCache = hashToScalar(concat(hashCache.bytes,proof.taux.bytes));
        hashCache = hashToScalar(concat(hashCache.bytes,proof.mu.bytes));
        hashCache = hashToScalar(concat(hashCache.bytes,proof.t.bytes));
        Scalar x_ip = hashCache;

        // PAPER LINE 61
        Curve25519Point L61Left = G.scalarMultiply(proof.taux).add(H.scalarMultiply(proof.t));

        Scalar k = ComputeK(y,z);

        Curve25519Point L61Right = H.scalarMultiply(k.add(z.mul(InnerProduct(VectorPowers(Scalar.ONE),VectorPowers(y)))));
        L61Right = L61Right.add(proof.V.scalarMultiply(z.sq()));
        L61Right = L61Right.add(proof.T1.scalarMultiply(x));
        L61Right = L61Right.add(proof.T2.scalarMultiply(x.sq()));

        if (!L61Right.equals(L61Left))
            return false;

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

        // Compute the number of rounds for the inner product
        int rounds = proof.L.length;

        // PAPER LINES 21-22
        // The inner product challenges are computed per round
        Scalar[] w = new Scalar[rounds];
        hashCache = hashToScalar(concat(hashCache.bytes,proof.L[0].toBytes()));
        hashCache = hashToScalar(concat(hashCache.bytes,proof.R[0].toBytes()));
        w[0] = hashCache;
        if (rounds > 1)
        {
            for (int i = 1; i < rounds; i++)
            {
                hashCache = hashToScalar(concat(hashCache.bytes,proof.L[i].toBytes()));
                hashCache = hashToScalar(concat(hashCache.bytes,proof.R[i].toBytes()));
                w[i] = hashCache;
            }
        }

        // Basically PAPER LINES 24-25
        // Compute the curvepoints from G[i] and H[i]
        Curve25519Point InnerProdG = Curve25519Point.ZERO;
        Curve25519Point InnerProdH = Curve25519Point.ZERO;
        for (int i = 0; i < N; i++)
        {
            // Convert the index to binary IN REVERSE and construct the scalar exponent
            int index = i;
            Scalar gScalar = Scalar.ONE;
            Scalar hScalar = Invert(y).pow(i);

            for (int j = rounds-1; j >= 0; j--)
            {
                int J = w.length - j - 1; // because this is done in reverse bit order
                int basePow = (int) Math.pow(2,j); // assumes we don't get too big
                if (index / basePow == 0) // bit is zero
                {
                    gScalar = gScalar.mul(Invert(w[J]));
                    hScalar = hScalar.mul(w[J]);
                }
                else // bit is one
                {
                    gScalar = gScalar.mul(w[J]);
                    hScalar = hScalar.mul(Invert(w[J]));
                    index -= basePow;
                }
            }

            // Now compute the basepoint's scalar multiplication
            // Each of these could be written as a multiexp operation instead
            InnerProdG = InnerProdG.add(Gi[i].scalarMultiply(gScalar));
            InnerProdH = InnerProdH.add(Hi[i].scalarMultiply(hScalar));
        }

        // PAPER LINE 26
        Curve25519Point Pprime = P.add(G.scalarMultiply(Scalar.ZERO.sub(proof.mu)));

        for (int i = 0; i < rounds; i++)
        {
            Pprime = Pprime.add(proof.L[i].scalarMultiply(w[i].sq()));
            Pprime = Pprime.add(proof.R[i].scalarMultiply(Invert(w[i]).sq()));
        }
        Pprime = Pprime.add(H.scalarMultiply(proof.t.mul(x_ip)));

        if (!Pprime.equals(InnerProdG.scalarMultiply(proof.a).add(InnerProdH.scalarMultiply(proof.b)).add(H.scalarMultiply(proof.a.mul(proof.b).mul(x_ip)))))
            return false;

        return true;
    }

    public static void main(String[] args)
    {
        // Number of bits in the range
        N = 64;
        logN = 6; // its log, manually

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
