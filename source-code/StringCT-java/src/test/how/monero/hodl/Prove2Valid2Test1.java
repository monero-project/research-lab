package test.how.monero.hodl;

import how.monero.hodl.crypto.Curve25519PointPair;
import how.monero.hodl.crypto.Scalar;

import static how.monero.hodl.crypto.CryptoUtil.COMeg;
import static how.monero.hodl.ringSignature.StringCT.*;

public class Prove2Valid2Test1 {

  public static void main(String[] args) {

    System.out.println("Test: " + new Object(){}.getClass().getEnclosingClass().getName());

    // [c[0], c[1]] = [ COMeg(0, r), COMeg(1, s) ] with secret index 0 should PASS
    Scalar r = Scalar.ONE;
    Scalar s = Scalar.ONE;

    Curve25519PointPair[] co = new Curve25519PointPair[]{
      COMeg(Scalar.ZERO, r),
      COMeg(Scalar.ONE, s)
    };

    int iAsterisk = 0;

    int inputs = 1;
    int decompositionBase = 2;
    int decompositionExponent = 1;

    Proof2 P2 = PROVE2(co, iAsterisk, r, inputs, decompositionBase, decompositionExponent);

    System.out.println("VALID2 result: " + VALID2(decompositionBase, P2, co));

  }


}
