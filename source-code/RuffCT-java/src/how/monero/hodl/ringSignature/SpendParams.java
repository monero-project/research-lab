package how.monero.hodl.ringSignature;

import how.monero.hodl.crypto.Curve25519Point;
import how.monero.hodl.crypto.Curve25519PointPair;
import how.monero.hodl.crypto.Scalar;

public class SpendParams {

  public int iAsterisk;
  public Curve25519PointPair[][] pk;
  public StringCT.SK[] sk;
  public Curve25519Point[] ki;
  public Curve25519Point[] co;
  public byte[] M;
  public Scalar s;
  public int decompositionBase;
  public int decompositionExponent;

}
