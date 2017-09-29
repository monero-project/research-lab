package how.monero.hodl.crypto;

import org.nem.core.crypto.ed25519.arithmetic.Ed25519EncodedGroupElement;
import org.nem.core.crypto.ed25519.arithmetic.Ed25519GroupElement;
import org.nem.core.utils.ArrayUtils;

import java.math.BigInteger;

import static how.monero.hodl.crypto.CryptoUtil.*;
import static how.monero.hodl.util.ByteUtil.*;

public class HashToPoint {

  private static BigInteger b = BigInteger.valueOf(256);
  private static BigInteger q = BigInteger.valueOf(2).pow(255).subtract(BigInteger.valueOf(19));
  private static BigInteger p = q;
  private static BigInteger l = BigInteger.valueOf(2).pow(252).add(new BigInteger("27742317777372353535851937790883648493"));
  private static BigInteger I = expmod(BigInteger.valueOf(2), (q.subtract(BigInteger.ONE)).divide(BigInteger.valueOf(4)), q);


  public static Ed25519GroupElement hashToPoint(Ed25519GroupElement a) {
    return hashToPoint(a.encode().getRaw());
  }

  public static Ed25519GroupElement hashToPoint(byte[] a) {

    byte[] hash = fastHash(a);

    BigInteger u = ArrayUtils.toBigInteger(hash).mod(q);

    BigInteger A = BigInteger.valueOf(486662);

    BigInteger sqrtm1 = ed25519Sqroot(BigInteger.valueOf(-1));

    BigInteger w = (BigInteger.valueOf(2).multiply(u).multiply(u).add(BigInteger.ONE)).mod(q);
    BigInteger xp = w.multiply(w).subtract(BigInteger.valueOf(2).multiply(A).multiply(A).multiply(u).multiply(u)).mod(q);

    BigInteger b = w.multiply(ed25519Inv(xp));
    BigInteger e = (q.add(BigInteger.valueOf(3)).divide(BigInteger.valueOf(8)));
    BigInteger rx = expmod(b, e, q);

    BigInteger x = rx.multiply(rx).multiply(w.multiply(w).subtract(BigInteger.valueOf(2).multiply(A).multiply(A).multiply(u).multiply(u))).mod(q);

    BigInteger y = (BigInteger.valueOf(2).multiply(u).multiply(u).add(BigInteger.ONE).subtract(x)).mod(q);

    BigInteger z;

    boolean negative = false;
    if (!y.equals(BigInteger.ZERO)) {
      y = (w.add(x)).mod(q);
      if (!y.equals(BigInteger.ZERO)) {
        negative = true;
      } else {
        rx = rx.multiply(BigInteger.valueOf(-1)).multiply(ed25519Sqroot(BigInteger.valueOf(-2).multiply(A).multiply((A.add(BigInteger.valueOf(2)))))).mod(q);
        negative = false;
      }
    } else {
      rx = rx.multiply(BigInteger.valueOf(-1)).multiply(ed25519Sqroot(BigInteger.valueOf(2).multiply(A).multiply((A.add(BigInteger.valueOf(2)))))).mod(q);
    }

    BigInteger sign;
    if (!negative) {
      rx = (rx.multiply(u)).mod(q);
      z = (BigInteger.valueOf(-2).multiply(A).multiply(u).multiply(u)).mod(q);
      sign = BigInteger.ZERO;
    } else {
      z = BigInteger.valueOf(-1).multiply(A);
      x = x.multiply(sqrtm1).mod(q);
      y = (w.subtract(x)).mod(q);
      if (!y.equals(BigInteger.ZERO)) {
        rx = rx.multiply(ed25519Sqroot(BigInteger.valueOf(-1).multiply(sqrtm1).multiply(A).multiply((A.add(BigInteger.valueOf(2)))))).mod(q);
      } else {
        rx = rx.multiply(BigInteger.valueOf(-1)).multiply(ed25519Sqroot(sqrtm1.multiply(A).multiply((A.add(BigInteger.valueOf(2)))))).mod(q);
      }
      sign = BigInteger.ONE;
    }
    if(!(rx.mod(BigInteger.valueOf(2)).equals(sign))) {
      rx = rx.mod(q).negate();
    }
    BigInteger rz = (z.add(w)).mod(q);
    BigInteger ry = (z.subtract(w)).mod(q);
    rx = (rx.multiply(rz)).mod(q);

    Ed25519GroupElement P = pointCompress(rx, ry, rz);
    Ed25519GroupElement P8 = P.toP2().dbl().toP2().dbl().toP2().dbl().toP3();
    return P8;

  }

  private static Ed25519GroupElement pointCompress(BigInteger P0, BigInteger P1, BigInteger P2) {
    BigInteger zinv = modpInv(P2);
    BigInteger x = P0.multiply(zinv).mod(p);
    BigInteger y = P1.multiply(zinv).mod(p);

    BigInteger r = y.or((x.and(BigInteger.ONE)).shiftLeft(255));

    byte[] a = r.toByteArray();

    byte[] b = new byte[32];

    if(a.length>32) System.arraycopy(a, a.length-32, b, 0, 32);
    else if(a.length<32) System.arraycopy(a, 0, b, 32-a.length, a.length);
    else System.arraycopy(a, 0, b, 0, 32);

    reverseByteArrayInPlace(b);
    return new Ed25519EncodedGroupElement(b).decode();
  }

  private static BigInteger modpInv(BigInteger x) {
    return x.modPow(p.subtract(BigInteger.valueOf(2)), p);
  }

  private static BigInteger ed25519Inv(BigInteger x) {
    return expmod(x, q.subtract(BigInteger.valueOf(2)), q);
  }

  private static BigInteger ed25519Sqroot(BigInteger xx) {
    BigInteger x = expmod(xx, q.add(BigInteger.valueOf(3)).divide(BigInteger.valueOf(8)), q);
    if (!x.multiply(x).subtract(xx).mod(q).equals(BigInteger.ZERO)) {
      x = x.multiply(I).mod(q);
    }
    if (!x.multiply(x).subtract(xx).mod(q).equals(BigInteger.ZERO)) {
      throw new RuntimeException("no square root!");
    }
    return x;
  }

  private static BigInteger expmod(BigInteger b, BigInteger e, BigInteger m) {
    if (e.equals(BigInteger.ZERO)) return BigInteger.ONE;
    BigInteger t = expmod(b, e.divide(BigInteger.valueOf(2)), m).pow(2).mod(m);
    if(e.and(BigInteger.ONE).equals(BigInteger.ONE)) t = (t.multiply(b)).mod(m);
    return t;
  }


}
