package how.monero.hodl.crypto;

import how.monero.hodl.util.ByteUtil;
import org.nem.core.crypto.ed25519.arithmetic.Ed25519EncodedFieldElement;
import org.nem.core.crypto.ed25519.arithmetic.Ed25519FieldElement;

import java.math.BigInteger;
import java.util.Arrays;

import static how.monero.hodl.crypto.CryptoUtil.*;
import static how.monero.hodl.util.ByteUtil.*;

public class Scalar {

  public final static Scalar ZERO = intToScalar(0);
  public final static Scalar ONE = intToScalar(1);
  public final static Scalar TWO = intToScalar(2);
  public final static Scalar MINUS_ONE = intToScalar(-1);

  // use only for small numbers
  public static Scalar intToScalar(int a) {
    return new Scalar(scReduce32(getUnsignedLittleEndianByteArrayFromBigInteger(BigInteger.valueOf(a).mod(l))));
  }

  public byte[] bytes;
  public Scalar(byte[] bytes) {
    this.bytes = bytes;
  }
  public Scalar(String hex) {
    this.bytes = ByteUtil.hexToBytes(hex);
  }
  public Scalar(BigInteger a) {
    this(scReduce32(getUnsignedLittleEndianByteArrayFromBigInteger(a.mod(l))));
  }
  public Ed25519EncodedFieldElement toEd25519EncodedFieldElement() {
    return new Ed25519EncodedFieldElement(bytes);
  }
  public Ed25519FieldElement toEd25519FieldElement() {
    return new Ed25519EncodedFieldElement(bytes).decode();
  }

  public static Scalar randomScalar() {
    byte[] s = new byte[32];
    random.nextBytes(s);
    s = CryptoUtil.scReduce32(s);
    return new Scalar(s);
  }

  @Override
  public String toString() {
    return bytesToHex(bytes);
  }

  public BigInteger toBigInteger() {
    return getBigIntegerFromUnsignedLittleEndianByteArray(this.bytes);
  }

  @Override
  public boolean equals(Object obj) {
    return Arrays.equals(this.bytes, ((Scalar)obj).bytes);
  }

  public static BigInteger[] scalarArrayToBigIntegerArray(Scalar[] a) {
    BigInteger[] r = new BigInteger[a.length];
    for(int i=0; i<a.length; i++) r[i] = a[i].toBigInteger();
    return r;
  }

  public static void printScalarArray(Scalar[] a) {
    for(int i=0; i<a.length; i++) {
      System.out.print(a[i].toBigInteger()+"");
      if(i==a.length-1) System.out.println("");
      else System.out.print(", ");
    }
  }

  public static Scalar[] bigIntegerArrayToScalarArray(BigInteger[] a) {
    int len = a.length;
    Scalar[] r = new Scalar[len];
    for(int i=0; i<len; i++) {
      r[i] = new Scalar(a[i]);
    }
    return r;
  }

  public Scalar add(Scalar a) { return new Scalar(ensure32BytesAndConvertToLittleEndian(getBigIntegerFromUnsignedLittleEndianByteArray(this.bytes).add(getBigIntegerFromUnsignedLittleEndianByteArray(a.bytes)).mod(l).toByteArray())); }
  public Scalar sub(Scalar a) { return new Scalar(ensure32BytesAndConvertToLittleEndian(getBigIntegerFromUnsignedLittleEndianByteArray(this.bytes).subtract(getBigIntegerFromUnsignedLittleEndianByteArray(a.bytes)).mod(l).toByteArray())); }
  public Scalar mul(Scalar a) { return new Scalar(ensure32BytesAndConvertToLittleEndian(getBigIntegerFromUnsignedLittleEndianByteArray(this.bytes).multiply(getBigIntegerFromUnsignedLittleEndianByteArray(a.bytes)).mod(l).toByteArray())); }
  public Scalar sq() { return new Scalar(ensure32BytesAndConvertToLittleEndian(getBigIntegerFromUnsignedLittleEndianByteArray(this.bytes).multiply(getBigIntegerFromUnsignedLittleEndianByteArray(this.bytes)).mod(l).toByteArray())); }

  public Scalar pow(int b) {
    Scalar result = Scalar.ONE;
    for(int i=0; i<b; i++) {
      result = result.mul(this);
    }
    return result;
  }


}
