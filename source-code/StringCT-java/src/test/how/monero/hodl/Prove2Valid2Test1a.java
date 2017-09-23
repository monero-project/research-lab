package test.how.monero.hodl;

import how.monero.hodl.crypto.Curve25519PointPair;
import how.monero.hodl.crypto.Scalar;

import static how.monero.hodl.crypto.CryptoUtil.COMeg;
import static how.monero.hodl.ringSignature.StringCT.*;

public class Prove2Valid2Test1a {

  public static void main(String[] args) {

    System.out.println("Test: " + new Object(){}.getClass().getEnclosingClass().getName());

    Scalar r = Scalar.ONE;

    Curve25519PointPair[] co = new Curve25519PointPair[]{
      COMeg(Scalar.ONE,Scalar.ONE),
      COMeg(Scalar.ONE,Scalar.ONE),
      COMeg(Scalar.ONE,Scalar.ONE),
      COMeg(Scalar.ONE,Scalar.ONE),
      COMeg(Scalar.ONE,Scalar.ONE),
      COMeg(Scalar.ZERO, Scalar.ONE),
      COMeg(Scalar.ONE,Scalar.ONE),
      COMeg(Scalar.ONE,Scalar.ONE),
      COMeg(Scalar.ONE,Scalar.ONE),
    };

    int iAsterisk = 5;

    int inputs = 1;
    int decompositionBase = 3;
    int decompositionExponent = 2;

    Proof2 P2 = PROVE2(co, iAsterisk, r, inputs, decompositionBase, decompositionExponent);

    System.out.println("VALID2 result: " + VALID2(decompositionBase, P2, co));

  }


}
