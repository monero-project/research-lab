package how.monero.hodl.crypto;

import org.nem.core.crypto.ed25519.arithmetic.Ed25519GroupElement;

import static how.monero.hodl.util.ByteUtil.*;

public class PointPair {
  public Ed25519GroupElement P1;
  public Ed25519GroupElement P2;
  public PointPair(Ed25519GroupElement P1, Ed25519GroupElement P2) {
    this.P1 = P1;
    this.P2 = P2;
  }
  public byte[] toBytes() {
    return concat(P1.encode().getRaw(), P2.encode().getRaw());
  }
  public PointPair add(PointPair a) {
    return new PointPair(P1.toP3().add(a.P1.toP3().toCached()), P2.toP3().add(a.P2.toP3().toCached()));
  }
  public PointPair subtract(PointPair a) {
    return new PointPair(P1.toP3().subtract(a.P1.toCached()), P2.toP3().subtract(a.P2.toCached()));
  }
  public PointPair multiply(Scalar n) {
    return new PointPair(P1.toP3().scalarMultiply(n), P2.toP3().scalarMultiply(n));
  }

  public boolean equals(PointPair obj) {
    return P1.toP3().equals(obj.P1.toP3()) && P2.toP3().equals(obj.P2.toP3());
  }

  @Override
  public String toString() {
    return "(P1: " + bytesToHex(P1.encode().getRaw()) + ", P2: " + P2 + ")";
  }

}

