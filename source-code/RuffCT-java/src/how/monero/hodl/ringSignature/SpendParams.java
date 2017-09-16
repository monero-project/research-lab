package how.monero.hodl.ringSignature;

import how.monero.hodl.crypto.PointPair;
import how.monero.hodl.crypto.Scalar;
import org.nem.core.crypto.ed25519.arithmetic.Ed25519GroupElement;

public class SpendParams {

  public int iAsterisk;
  public PointPair[][] pk;
  public BootleRuffing.SK[] sk;
  public Ed25519GroupElement[] ki;
  public Ed25519GroupElement[] co;
  public byte[] M;
  public Scalar s;
  public int decompositionBase;
  public int decompositionExponent;

}
