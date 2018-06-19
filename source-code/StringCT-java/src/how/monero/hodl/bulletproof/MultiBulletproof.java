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

public class MultiBulletproof
{
    private static int NEXP;
    private static int N;
    private static Curve25519Point G;
    private static Curve25519Point H;
    private static Curve25519Point[] Gi;
    private static Curve25519Point[] Hi;

    public static class ProofTuple
    {
        private Curve25519Point V[];
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

        public ProofTuple(Curve25519Point V[], Curve25519Point A, Curve25519Point S, Curve25519Point T1, Curve25519Point T2, Scalar taux, Scalar mu, Curve25519Point[] L, Curve25519Point[] R, Scalar a, Scalar b, Scalar t)
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
        assert a.length == b.length;

        Curve25519Point Result = Curve25519Point.ZERO;
        for (int i = 0; i < a.length; i++)
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
    public static Scalar[] VectorPowers(Scalar x, int size)
    {
        Scalar[] result = new Scalar[size];
        for (int i = 0; i < size; i++)
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

    /* Construct an aggregate range proof */
    public static ProofTuple PROVE(Scalar[] v, Scalar[] gamma, int logM)
    {
        int M = v.length;
        int logMN = logM + NEXP;

        Curve25519Point[] V = new Curve25519Point[M];

        V[0] = H.scalarMultiply(v[0]).add(G.scalarMultiply(gamma[0]));
        // This hash is updated for Fiat-Shamir throughout the proof
        Scalar hashCache = hashToScalar(V[0].toBytes());
        for (int j = 1; j < M; j++)
        {
            V[j] = H.scalarMultiply(v[j]).add(G.scalarMultiply(gamma[j]));
            hashCache = hashToScalar(concat(hashCache.bytes,V[j].toBytes()));
        }
        
        // PAPER LINES 36-37
        Scalar[] aL = new Scalar[M*N];
        Scalar[] aR = new Scalar[M*N];

        for (int j = 0; j < M; j++)
        {
            BigInteger tempV = v[j].toBigInteger();
            for (int i = N-1; i >= 0; i--)
            {
                BigInteger basePow = BigInteger.valueOf(2).pow(i);
                if (tempV.divide(basePow).equals(BigInteger.ZERO))
                {
                    aL[j*N+i] = Scalar.ZERO;
                }
                else
                {
                    aL[j*N+i] = Scalar.ONE;
                    tempV = tempV.subtract(basePow);
                }

                aR[j*N+i] = aL[j*N+i].sub(Scalar.ONE);
            }
        }

        // PAPER LINES 38-39
        Scalar alpha = randomScalar();
        Curve25519Point A = VectorExponent(aL,aR).add(G.scalarMultiply(alpha));

        // PAPER LINES 40-42
        Scalar[] sL = new Scalar[M*N];
        Scalar[] sR = new Scalar[M*N];
        for (int i = 0; i < M*N; i++)
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

        // Polynomial construction by coefficients
        Scalar[] l0;
        Scalar[] l1;
        Scalar[] r0;
        Scalar[] r1;

        l0 = VectorSubtract(aL,VectorScalar(VectorPowers(Scalar.ONE,M*N),z));
        l1 = sL;

        // This computes the ugly sum/concatenation from PAPER LINE 65
        Scalar[] zerosTwos = new Scalar[M*N];
        for (int i = 0; i < M*N; i++)
        {
            zerosTwos[i] = Scalar.ZERO;
            for (int j = 1; j <= M; j++) // note this starts from 1
            {
                Scalar temp = Scalar.ZERO;
                if (i >= (j-1)*N && i < j*N)
                    temp = Scalar.TWO.pow(i-(j-1)*N); // exponent ranges from 0..N-1
                zerosTwos[i] = zerosTwos[i].add(z.pow(1+j).mul(temp));
            }
        }

        r0 = VectorAdd(aR,VectorScalar(VectorPowers(Scalar.ONE,M*N),z));
        r0 = Hadamard(r0,VectorPowers(y,M*N));
        r0 = VectorAdd(r0,zerosTwos);
        r1 = Hadamard(VectorPowers(y,M*N),sR);

        // Polynomial construction before PAPER LINE 46
        Scalar t0 = InnerProduct(l0,r0);
        Scalar t1 = InnerProduct(l0,r1).add(InnerProduct(l1,r0));
        Scalar t2 = InnerProduct(l1,r1);
        
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
        Scalar taux = tau1.mul(x);
        taux = taux.add(tau2.mul(x.sq()));
        for (int j = 1; j <= M; j++) // note this starts from 1
        {
            taux = taux.add(z.pow(1+j).mul(gamma[j-1]));
        }
        Scalar mu = x.mul(rho).add(alpha);

        // PAPER LINES 54-57
        Scalar[] l = l0;
        l = VectorAdd(l,VectorScalar(l1,x));
        Scalar[] r = r0;
        r = VectorAdd(r,VectorScalar(r1,x));

        Scalar t = InnerProduct(l,r);

        // PAPER LINES 32-33
        hashCache = hashToScalar(concat(hashCache.bytes,x.bytes));
        hashCache = hashToScalar(concat(hashCache.bytes,taux.bytes));
        hashCache = hashToScalar(concat(hashCache.bytes,mu.bytes));
        hashCache = hashToScalar(concat(hashCache.bytes,t.bytes));
        Scalar x_ip = hashCache;

        // These are used in the inner product rounds
        int nprime = M*N;
        Curve25519Point[] Gprime = new Curve25519Point[M*N];
        Curve25519Point[] Hprime = new Curve25519Point[M*N];
        Scalar[] aprime = new Scalar[M*N];
        Scalar[] bprime = new Scalar[M*N];
        for (int i = 0; i < M*N; i++)
        {
            Gprime[i] = Gi[i];
            Hprime[i] = Hi[i].scalarMultiply(Invert(y).pow(i));
            aprime[i] = l[i];
            bprime[i] = r[i];
        }
        Curve25519Point[] L = new Curve25519Point[logMN];
        Curve25519Point[] R = new Curve25519Point[logMN];
        int round = 0; // track the index based on number of rounds
        Scalar[] w = new Scalar[logMN]; // this is the challenge x in the inner product protocol

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
    public static boolean VERIFY(ProofTuple[] proofs)
    {
        // Figure out which proof is longest
        int maxLength = 0;
        for (int p = 0; p < proofs.length; p++)
        {
            if (proofs[p].L.length > maxLength)
                maxLength = proofs[p].L.length;
        }
        int maxMN = (int) Math.pow(2,maxLength);

        // Set up weighted aggregates for the first check
        Scalar y0 = Scalar.ZERO; // tau_x
        Scalar y1 = Scalar.ZERO; // t-(k+z+Sum(y^i))
        Curve25519Point Y2 = Curve25519Point.ZERO; // z-V sum
        Curve25519Point Y3 = Curve25519Point.ZERO; // xT_1
        Curve25519Point Y4 = Curve25519Point.ZERO; // x^2T_2
        
        
        // Set up weighted aggregates for the second check
        Curve25519Point Z0 = Curve25519Point.ZERO; // A + xS
        Scalar z1 = Scalar.ZERO; // mu
        Curve25519Point Z2 = Curve25519Point.ZERO; // Li/Ri sum
        Scalar z3 = Scalar.ZERO; // (t-ab)x_ip
        Scalar[] z4 = new Scalar[maxMN]; // g scalar sum
        Scalar[] z5 = new Scalar[maxMN]; // h scalar sum

        for (int i = 0; i < maxMN; i++)
        {
            z4[i] = Scalar.ZERO;
            z5[i] = Scalar.ZERO;
        }

        for (int p = 0; p < proofs.length; p++)
        {
            ProofTuple proof = proofs[p];
            int logMN = proof.L.length;
            int M = (int) Math.pow(2,logMN)/N;

            // For the current proof, get a random weighting factor
            // NOTE: This must not be deterministic! Only the verifier knows it
            Scalar weight = randomScalar();

            // Reconstruct the challenges
            Scalar hashCache = hashToScalar(proof.V[0].toBytes());
            for (int j = 1; j < M; j++)
                hashCache = hashToScalar(concat(hashCache.bytes,proof.V[j].toBytes()));
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
            y0 = y0.add(proof.taux.mul(weight));
            
            Scalar k = Scalar.ZERO.sub(z.sq().mul(InnerProduct(VectorPowers(Scalar.ONE,M*N),VectorPowers(y,M*N))));
            for (int j = 1; j <= M; j++) // note this starts from 1
            {
                k = k.sub(z.pow(j+2).mul(InnerProduct(VectorPowers(Scalar.ONE,N),VectorPowers(Scalar.TWO,N))));
            }

            y1 = y1.add(proof.t.sub(k.add(z.mul(InnerProduct(VectorPowers(Scalar.ONE,M*N),VectorPowers(y,M*N))))).mul(weight));
            
            Curve25519Point temp = Curve25519Point.ZERO;
            for (int j = 0; j < M; j++)
            {
                temp = temp.add(proof.V[j].scalarMultiply(z.pow(j+2)));
            }
            Y2 = Y2.add(temp.scalarMultiply(weight));
            Y3 = Y3.add(proof.T1.scalarMultiply(x.mul(weight)));
            Y4 = Y4.add(proof.T2.scalarMultiply(x.sq().mul(weight)));
            
            // PAPER LINE 62
            Z0 = Z0.add((proof.A.add(proof.S.scalarMultiply(x))).scalarMultiply(weight));
            
            // PAPER LINES 21-22
            // The inner product challenges are computed per round
            Scalar[] w = new Scalar[logMN];
            hashCache = hashToScalar(concat(hashCache.bytes,proof.L[0].toBytes()));
            hashCache = hashToScalar(concat(hashCache.bytes,proof.R[0].toBytes()));
            w[0] = hashCache;
            if (logMN > 1)
            {
                for (int i = 1; i < logMN; i++)
                {
                    hashCache = hashToScalar(concat(hashCache.bytes,proof.L[i].toBytes()));
                    hashCache = hashToScalar(concat(hashCache.bytes,proof.R[i].toBytes()));
                    w[i] = hashCache;
                }
            }

            // Basically PAPER LINES 24-25
            // Compute the curvepoints from G[i] and H[i]
            for (int i = 0; i < M*N; i++)
            {
                // Convert the index to binary IN REVERSE and construct the scalar exponent
                int index = i;
                Scalar gScalar = proof.a;
                Scalar hScalar = proof.b.mul(Invert(y).pow(i));
                
                for (int j = logMN-1; j >= 0; j--)
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
                
                gScalar = gScalar.add(z);
                hScalar = hScalar.sub(z.mul(y.pow(i)).add(z.pow(2+i/N).mul(Scalar.TWO.pow(i%N))).mul(Invert(y).pow(i)));

                // Now compute the basepoint's scalar multiplication
                z4[i] = z4[i].add(gScalar.mul(weight));
                z5[i] = z5[i].add(hScalar.mul(weight));
            }

            // PAPER LINE 26
            z1 = z1.add(proof.mu.mul(weight));

            temp = Curve25519Point.ZERO;
            for (int i = 0; i < logMN; i++)
            {
                temp = temp.add(proof.L[i].scalarMultiply(w[i].sq()));
                temp = temp.add(proof.R[i].scalarMultiply(Invert(w[i]).sq()));
            }
            Z2 = Z2.add(temp.scalarMultiply(weight));
            z3 = z3.add((proof.t.sub(proof.a.mul(proof.b))).mul(x_ip).mul(weight));

        }

        // Perform the first- and second-stage check on all proofs at once
        // NOTE: These checks could benefit from multiexp operations
        Curve25519Point Check1 = Curve25519Point.ZERO;
        Check1 = Check1.add(G.scalarMultiply(y0));
        Check1 = Check1.add(H.scalarMultiply(y1));
        Check1 = Check1.add(Y2.scalarMultiply(Scalar.ZERO.sub(Scalar.ONE)));
        Check1 = Check1.add(Y3.scalarMultiply(Scalar.ZERO.sub(Scalar.ONE)));
        Check1 = Check1.add(Y4.scalarMultiply(Scalar.ZERO.sub(Scalar.ONE)));
        if (! Check1.equals(Curve25519Point.ZERO))
        {
            System.out.println("Failed first-stage check");
            return false;
        }

        Curve25519Point Check2 = Curve25519Point.ZERO;
        Check2 = Check2.add(Z0);
        Check2 = Check2.add(G.scalarMultiply(Scalar.ZERO.sub(z1)));
        Check2 = Check2.add(Z2);
        Check2 = Check2.add(H.scalarMultiply(z3));

        for (int i = 0; i < maxMN; i++)
        {
            Check2 = Check2.add(Gi[i].scalarMultiply(Scalar.ZERO.sub(z4[i])));
            Check2 = Check2.add(Hi[i].scalarMultiply(Scalar.ZERO.sub(z5[i])));
        }

        if (! Check2.equals(Curve25519Point.ZERO))
        {
            System.out.println("Failed second-stage check");
            return false;
        }

        return true;
    }

    /* Generate a random proof with specified bit size and number of outputs */
    public static ProofTuple randomProof(int mExp)
    {
        int M = (int) Math.pow(2,mExp);

        Random rando = new Random();
        Scalar[] amounts = new Scalar[M];
        Scalar[] masks = new Scalar[M];

        // Generate the outputs and masks
        for (int i = 0; i < M; i++)
        {
            long amount = -1L;
            while (amount > Math.pow(2,N)-1 || amount < 0L) // Java doesn't handle random long ranges very well
                amount = rando.nextLong();
            amounts[i] = new Scalar(BigInteger.valueOf(amount));
            masks[i] = randomScalar();
        }
        
        // Run and return the proof
        // Have to pass in lg(M) because Java is stupid about logarithms
        System.out.println("Generating proof with " + M + " outputs...");
        return PROVE(amounts,masks,mExp);
    }

    public static void main(String[] args)
    {
        // Test parameters: currently only works when batching proofs of the same aggregation size
        NEXP = 6; // N = 2^NEXP
        N = (int) Math.pow(2,NEXP); // number of bits in amount range (so amounts are 0..2^(N-1))
        int MAXEXP = 4; // the maximum number of outputs used is 2^MAXEXP
        int PROOFS = 5; // number of proofs in batch

        // Set the curve base points
        G = Curve25519Point.G;
        H = Curve25519Point.hashToPoint(G);
        int MAXM = (int) Math.pow(2,MAXEXP);
        Gi = new Curve25519Point[MAXM*N];
        Hi = new Curve25519Point[MAXM*N];
        for (int i = 0; i < MAXM*N; i++)
        {
            Gi[i] = getHpnGLookup(2*i);
            Hi[i] = getHpnGLookup(2*i+1);
        }
        
        // Set up all the proofs
        ProofTuple[] proofs = new ProofTuple[PROOFS];
        Random rando = new Random();
        for (int i = 0; i < PROOFS; i++)
        {
            // Pick a random proof length: 2^0,...,2^MAXEXP
            proofs[i] = randomProof(rando.nextInt(MAXEXP+1));
        }

        // Verify the batch
        System.out.println("Verifying proof batch...");
        if (VERIFY(proofs))
            System.out.println("Success!");
        else
            System.out.println("ERROR: failed verification");
            
    }
}
