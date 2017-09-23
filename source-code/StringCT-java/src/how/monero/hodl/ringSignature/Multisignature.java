package how.monero.hodl.ringSignature;

import how.monero.hodl.crypto.Curve25519Point;
import how.monero.hodl.crypto.Scalar;

import java.util.*;

import static how.monero.hodl.crypto.Scalar.randomScalar;
import static how.monero.hodl.util.ByteUtil.bytesToHex;
import static how.monero.hodl.util.ByteUtil.concat;
import static how.monero.hodl.crypto.CryptoUtil.*;

public class Multisignature {

  public static Curve25519Point[] lexicographicalSort(Curve25519Point[] X) {
    SortedMap<String, Curve25519Point> hexToPoint = new TreeMap<>();
    for(Curve25519Point Xi : X) hexToPoint.put(bytesToHex(Xi.toBytes()), Xi);
    return hexToPoint.values().stream().toArray(Curve25519Point[]::new);
  }

  /*
      VER*: Take as input a message M, public keys L' = X[1], ..., X[n], and a
      signature sigma = (R,s).
        1) Compute L* = H(L')
        2) For each i=1,2,...,n, compute c[i] = Hs(X[i], R, L*, M)
        3) Accept if and only if sG = R + c[1]*X[1] + ... + c[n]*X[n]
   */
  public static boolean verify(byte[] M, Curve25519Point[] X, Signature signature) {
    int n = X.length;

    Scalar XAsterisk = hashToScalar(toBytes(lexicographicalSort(X)));

    Scalar[] c = new Scalar[n];
    for(int i=0; i<n; i++) {
      c[i] = hashToScalar(concat(X[i].toBytes(), signature.R.toBytes(), XAsterisk.bytes, M));
    }
    Curve25519Point sG = Curve25519Point.G.scalarMultiply(signature.s);
    Curve25519Point sG1 = signature.R;
    for(int i=0; i<n; i++) sG1 = sG1.add(X[i].scalarMultiply(c[i]));
    return sG.equals(sG1);
  }

  /*
    SIG*: Take as input a message M and a list of private keys L = x[0], x[1],
    ..., x[n-1]. Let L' be the associated list of public keys X[0], ..., X[n-1], and
    assume L' is lexicographically ordered.
      1) Compute L* = H(L').
      2) For each i=0,1,...,n-1, select r[i] at random from Zq.
      3) Compute r=r[0]+r[1]+...+r[n-1] and R=rG.
      4) For each i=0,1,...,n-1:
          i)  Compute c[i] := Hs(X[i], R, L*, M)
          ii) Compute s[i] := r[i] + x[i]*c[i]
      5) Compute s = s[1] + ... + s[n].
      6) Output the signature sigma = (R, s)
   */
  public static Signature sign(byte[] M, Scalar[] x, Curve25519Point[] X) {
    int n = x.length;
    if(X==null) {
      X = new Curve25519Point[n];
      for(int i=0; i<n; i++) {
        X[i] = Curve25519Point.G.scalarMultiply(x[i]);
      }

    }
    Scalar XAsterisk = hashToScalar(toBytes(lexicographicalSort(X)));

    Scalar[] rArray = new Scalar[n];
    for(int i=0; i<n; i++) rArray[i] = randomScalar();
    Scalar r = sumArray(rArray);

    Curve25519Point R = Curve25519Point.G.scalarMultiply(r);
    Scalar[] c = new Scalar[n];
    Scalar[] sArray = new Scalar[n];
    for(int i=0; i<n; i++) {
      c[i] = hashToScalar(concat(X[i].toBytes(), R.toBytes(), XAsterisk.bytes, M));
      sArray[i] = rArray[i].add(x[i].mul(c[i]));
    }
    Scalar s = sumArray(sArray);
    return new Signature(R, s);
  }

  public static class Signature {
    Curve25519Point R;
    Scalar s;
    public Signature(Curve25519Point R, Scalar s) {
      this.R = R; this.s = s;
    }
    public byte[] toBytes() {
      return concat(R.toBytes(), s.bytes);
    }
  }

  /*
      KEYGEN*: Each user selects x at random from Zq. The secret key is x. The
      public key is X=xG. Output (sk,pk) = (x,X).
   */
  public static KeyPair keygen() {
    Scalar x = randomScalar();
    Curve25519Point X = Curve25519Point.G.scalarMultiply(x);
    return new KeyPair(x, X);
  }
  public static class KeyPair {
    public Scalar x;
    public Curve25519Point X;
    public KeyPair(Scalar x, Curve25519Point X) {
      this.x = x; this.X = X;
    }
  }





}
