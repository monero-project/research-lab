package test.how.monero.hodl;

import how.monero.hodl.crypto.Scalar;
import org.nem.core.crypto.ed25519.arithmetic.Ed25519GroupElement;

import static how.monero.hodl.crypto.CryptoUtil.COMb;
import static how.monero.hodl.ringSignature.BootleRuffing.*;

public class Prove1Valid1Test1 {

  public static void main(String[] args) {

    Scalar[][] b = new Scalar[][] {
      new Scalar[]{Scalar.ONE, Scalar.ZERO},
      new Scalar[]{Scalar.ZERO, Scalar.ONE}
    };

    Scalar r = Scalar.ONE;

    Proof1 P = PROVE1(b, r);

    Ed25519GroupElement B = COMb(b, r);

    System.out.println("VALID1 returns " + VALID1(B, P));

  }


}
