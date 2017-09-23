package how.monero.hodl.util;

public class VarInt {

  public static byte[] writeVarInt(long value) {
    byte[] data = new byte[8];
    int pos = 0;

    while ((value & 0xFFFFFF80) != 0L) {
      data[pos] = (byte) ((value & 0x7F) | 0x80);
      pos++;
      value >>>= 7;
    }
    data[pos] = (byte) (value & 0x7F);
    pos++;

    byte[] result = new byte[pos];
    System.arraycopy(data, 0, result, 0, pos);
    return result;
  }

  public static long readVarInt(byte[] data) {

    long result = 0;
    int c = 0;
    int pos = 0;

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


}
