package test.how.monero.hodl;

import how.monero.hodl.crypto.PointPair;
import how.monero.hodl.crypto.Scalar;
import org.nem.core.crypto.ed25519.arithmetic.Ed25519GroupElement;

import java.util.Date;

import static how.monero.hodl.crypto.CryptoUtil.COMeg;
import static how.monero.hodl.ringSignature.BootleRuffing.*;

public class Prove2Valid2Test1b {

  public static void main(String[] args) {

    System.out.println("Test: " + new Object(){}.getClass().getEnclosingClass().getName());

    Scalar r = Scalar.ONE;

    for(int k=1; k<=64; k++) {

      System.out.println("---------------------------------------------------------------------------");
      int len = (int) Math.pow(2, k);
      PointPair[] co = new PointPair[len];
      for (int i = 0; i < len; i++) co[i] = COMeg(Scalar.intToScalar(i), Scalar.ONE);

      int iAsterisk = 0;

      int inputs = 1;
      int decompositionBase = 2;
      int decompositionExponent = k;

      System.out.println("k: " + k);
      System.out.println("decompositionBase: " + decompositionBase);
      System.out.println("decompositionExponent: " + decompositionExponent);

      Ed25519GroupElement.scalarMults = 0;
      Ed25519GroupElement.scalarBaseMults = 0;
      long startMs = new Date().getTime();

      Proof2 P2 = PROVE2(co, iAsterisk, r, inputs, decompositionBase, decompositionExponent);

      System.out.println("PROVE2 duration: " + (new Date().getTime() - startMs) + " ms");
      System.out.println("PROVE2 ScalarMults: " + Ed25519GroupElement.scalarMults);
      System.out.println("PROVE2 BaseScalarMults: " + Ed25519GroupElement.scalarBaseMults);
      Ed25519GroupElement.scalarMults = 0;
      Ed25519GroupElement.scalarBaseMults = 0;
      startMs = new Date().getTime();

      System.out.println("VALID2 result: " + VALID2(decompositionBase, P2, co));

      System.out.println("VALID2 ScalarMults: " + Ed25519GroupElement.scalarMults);
      System.out.println("VALID2 BaseScalarMults: " + Ed25519GroupElement.scalarBaseMults);

      System.out.println("VALID2 duration: " + (new Date().getTime() - startMs) + " ms");
    }

  }


}
