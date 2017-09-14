package how.monero.hodl.jni;

public class CryptoOpsUtil {

  static { System.loadLibrary("cryptoopsutil"); }

  public static native byte[] scalarMult(byte[] point, byte[] scalar);
  public static native byte[] scalarMultBase(byte[] scalar);
  public static native byte[] doubleScalarMultBaseVartime(byte[] aScalar, byte[] point, byte[] bScalar);

}
