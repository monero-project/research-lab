package how.monero.hodl.cursor;

import how.monero.hodl.crypto.Scalar;

import java.math.BigInteger;

public class Cursor {

  public int pos = 0;
  protected byte[] data;
  public Cursor(byte[] data) {
    this.data = data;
  }

  public long readVarInt() {

    long result = 0;
    int c = 0;

    while(true) {
      boolean isLastByteInVarInt = true;
      int i = Byte.toUnsignedInt(data[pos]);
      if(i>=128) {
        isLastByteInVarInt = false;
        i-=128;
      }
      result += Math.round(i * Math.pow(128, c));
      c++;
      pos++;
      if(isLastByteInVarInt) break;
    }
    return result;
  }
  public BigInteger readVarIntAsBigInteger() {

    BigInteger result = BigInteger.ZERO;
    int c = 0;

    while(true) {
      boolean isLastByteInVarInt = true;
      int i = Byte.toUnsignedInt(data[pos]);
      if(i>=128) {
        isLastByteInVarInt = false;
        i-=128;
      }
      result = result.add(BigInteger.valueOf(Math.round(i * Math.pow(128, c))));
      c++;
      pos++;
      if(isLastByteInVarInt) break;
    }
    return result;
  }

  public byte[] readBytes(int len) {
    byte[] bytes = new byte[len];
    System.arraycopy(data, pos, bytes, 0, len);
    pos+=len;
    return bytes;
  }
  public Scalar readScalar() {
    return new Scalar(readBytes(32));
  }


  public int readByte() {
    pos++;
    return Byte.toUnsignedInt(data[pos-1]);
  }

  public byte[] readKey() {
    return readBytes(32);
  }


}
