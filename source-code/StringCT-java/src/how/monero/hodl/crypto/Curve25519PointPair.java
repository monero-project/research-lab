package how.monero.hodl.crypto;

import static how.monero.hodl.util.ByteUtil.*;

public class Curve25519PointPair {
  public Curve25519Point P1;
  public Curve25519Point P2;
  public Curve25519PointPair(Curve25519Point P1, Curve25519Point P2) {
    this.P1 = P1;
    this.P2 = P2;
  }
  public byte[] toBytes() {
    return concat(P1.toBytes(), P2.toBytes());
  }
  public Curve25519PointPair add(Curve25519PointPair a) {
    return new Curve25519PointPair(P1.add(a.P1), P2.add(a.P2));
  }
  public Curve25519PointPair subtract(Curve25519PointPair a) {
    return new Curve25519PointPair(P1.subtract(a.P1), P2.subtract(a.P2));
  }
  public Curve25519PointPair multiply(Scalar n) {
    return new Curve25519PointPair(P1.scalarMultiply(n), P2.scalarMultiply(n));
  }

  public boolean equals(Curve25519PointPair obj) {
    return P1.equals(obj.P1) && P2.equals(obj.P2);
  }

  @Override
  public String toString() {
    return "(P1: " + bytesToHex(P1.toBytes()) + ", P2: " + P2 + ")";
  }

}

