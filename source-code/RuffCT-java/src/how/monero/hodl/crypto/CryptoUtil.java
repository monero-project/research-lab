package how.monero.hodl.crypto;

import com.joemelsha.crypto.hash.Keccak;
import how.monero.hodl.util.ExceptionAdapter;
import org.apache.commons.pool2.BasePooledObjectFactory;
import org.apache.commons.pool2.PooledObject;
import org.apache.commons.pool2.impl.DefaultPooledObject;
import org.apache.commons.pool2.impl.GenericObjectPool;
import org.nem.core.crypto.ed25519.arithmetic.*;

import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

import static how.monero.hodl.crypto.HashToPoint.hashToPoint;
import static how.monero.hodl.util.ByteUtil.*;

public class CryptoUtil {

  public static GenericObjectPool<Keccak> keccakPool = new GenericObjectPool<Keccak>(new BasePooledObjectFactory<Keccak>() {

    @Override
    public PooledObject<Keccak> wrap(Keccak keccak) {
      return new DefaultPooledObject<>(keccak);
    }

    @Override
    public Keccak create() throws Exception {
      return new Keccak(256);
    }
  });

  public static final Ed25519GroupElement G = Ed25519Group.BASE_POINT;
  public static final Ed25519GroupElement H = new Ed25519EncodedGroupElement(hexToBytes("8b655970153799af2aeadc9ff1add0ea6c7251d54154cfa92c173a0dd39c1f94")).decode();
  static {
    H.precomputeForScalarMultiplication();
  }

  public static Scalar hashToScalar(byte[] a) {
    return new Scalar(scReduce32(fastHash(a)));
  }

  public static byte[] fastHash(byte[] a) {
    try {
      Keccak keccak = keccakPool.borrowObject();
      try {
        keccak.reset();
        keccak.update(a);
        return keccak.digestArray();
      } finally {
        keccakPool.returnObject(keccak);
      }
    } catch (Exception e) {
      throw ExceptionAdapter.toRuntimeException(e);
    }
  }

  public static BigInteger l = BigInteger.valueOf(2).pow(252).add(new BigInteger("27742317777372353535851937790883648493"));

  public static byte[] scReduce32(byte[] a) {
    byte[] r = getBigIntegerFromUnsignedLittleEndianByteArray(a).mod(l).toByteArray();
    return ensure32BytesAndConvertToLittleEndian(r);
  }

  public static byte[] ensure32BytesAndConvertToLittleEndian(byte[] r) {
    byte[] s = new byte[32];
    if(r.length>32) System.arraycopy(r, 1, s, 0, s.length);
    else System.arraycopy(r, 0, s, 32 - r.length, r.length);
    reverseByteArrayInPlace(s);
    return s;
  }

  public static BigInteger getBigIntegerFromUnsignedLittleEndianByteArray(byte[] a1) {
    byte[] a = new byte[a1.length];
    System.arraycopy(a1, 0, a, 0, 32);
    reverseByteArrayInPlace(a);
    byte[] a2 = new byte[33];
    System.arraycopy(a, 0, a2, 1, 32);
    return new BigInteger(a2);
  }
  public static byte[] getUnsignedLittleEndianByteArrayFromBigInteger(BigInteger n) {
    byte[] a = n.toByteArray();
    byte[] a2 = new byte[32];
    System.arraycopy(a, 0, a2, 32-a.length, a.length);
    reverseByteArrayInPlace(a2);
    return a2;
  }

  public static final Random random = new SecureRandom();
  public static byte[] randomPointAsBytes() {
    return randomPoint().encode().getRaw();
  }
  public static Ed25519GroupElement randomPoint() {
    return Ed25519Group.BASE_POINT.scalarMultiply(Scalar.randomScalar());
  }
  public static byte[] randomMessage(int len) {
    byte[] m = new byte[len];
    random.nextBytes(m);
    return m;
  }

  public static byte[] toBytes(Ed25519GroupElement[] a) {
    byte[] r = new byte[0];
    for(Ed25519GroupElement ai : a) r = concat(r, ai.encode().getRaw());
    return r;
  }

  public static Scalar sumArray(Scalar[] a) {
    Scalar r = Scalar.ZERO;
    for(Scalar ai : a) r = r.add(ai);
    return r;
  }



  public static PointPair COMeg(Scalar xAmount, Scalar rMask) {
    return new PointPair(G.scalarMultiply(xAmount).add(getHpnGLookup(1).scalarMultiply(rMask).toCached()), G.scalarMultiply(rMask));
  }

  public static Ed25519GroupElement COMp(Scalar xAmount, Scalar rMask) {
    return G.scalarMultiply(xAmount).add(getHpnGLookup(1).scalarMultiply(rMask).toCached());
  }

  public static Ed25519GroupElement COMb(Scalar[][] x, Scalar r) {
    int m = x.length;
    int n = x[0].length;
    Ed25519GroupElement A = G.scalarMultiply(r);
    for(int j=0; j<m; j++) {
      for(int i=0; i<n; i++) {
        A = A.toP3().add(getHpnGLookup(j * n + i + 1).scalarMultiply(x[j][i]).toCached());
      }
    }
    return A;
  }


  public static Map<Integer, Ed25519GroupElement> HpnGLookup = new HashMap<>();

  public static Ed25519GroupElement getHpnGLookup(int n) {
    if(!HpnGLookup.containsKey(n)) {
      Ed25519GroupElement HpnG = hashToPoint(G.scalarMultiply(Scalar.intToScalar(n)));
      //HpnG.precomputeForScalarMultiplication(); // try precomputed vs non-precomputed to check best performance
      HpnGLookup.put(n, HpnG);
    }
    return HpnGLookup.get(n);
  }

  public static PointPair ENCeg(Ed25519GroupElement X, Scalar r) {
    return new PointPair(getHpnGLookup(1).scalarMultiply(r).toP3().add(X.toCached()), G.scalarMultiply(r));
  }


}
