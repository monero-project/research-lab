package test.how.monero.hodl;

import how.monero.hodl.crypto.Curve25519Point;
import how.monero.hodl.crypto.Curve25519PointPair;
import how.monero.hodl.crypto.Scalar;
import how.monero.hodl.ringSignature.SpendParams;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.Date;

import static how.monero.hodl.crypto.CryptoUtil.*;
import static how.monero.hodl.ringSignature.StringCT.*;

public class StringCTSpendTest {

  public static SpendParams createTestSpendParams(int decompositionBase, int decompositionExponent, int inputs) {

    // ring size must be a power of the decomposition base
    int ringSize = (int) Math.pow(decompositionBase, decompositionExponent);

    SpendParams sp = new SpendParams();

    sp.decompositionBase = decompositionBase;
    sp.decompositionExponent = decompositionExponent;

    // The owned inputs that are going to be spent
    Output[] realInputs = new Output[inputs];
    for(int i=0; i<inputs; i++) realInputs[i] = Output.genRandomOutput(BigInteger.valueOf((long)(Math.random()*1000+1000)));

    // The new outputs to be created (typically one for the recipient one for change)
    BigInteger fee = BigInteger.valueOf(0); //keep fee as zero for now, to avoid overcomplicating things
    Output[] outputs = new Output[2];
    outputs[0] = Output.genRandomOutput(realInputs[0].amount.divide(BigInteger.valueOf(2)));
    outputs[1] = Output.genRandomOutput(BigInteger.valueOf(Arrays.stream(realInputs).mapToLong(i->i.amount.longValue()).sum()).subtract(fee).subtract(outputs[0].amount));

    sp.iAsterisk = (int) Math.floor(Math.random()*ringSize); // the ring index of the sender's owned inputs

    // input commitments
    // commitments to the amounts of all inputs referenced in the transaction (real inputs and decoys)
    Curve25519Point[][] inputCommitments = new Curve25519Point[inputs][ringSize];
    for(int j=0; j<inputs; j++) {
      for(int i=0; i<ringSize; i++) {
        if(i==sp.iAsterisk) inputCommitments[j][i] = realInputs[j].co;
        else inputCommitments[j][i] = Curve25519Point.randomPoint();
      }
    }

    // there is a co commitment for each ring
    // each member of co is sum(COMp(input amt i)) - sum(COMp(output amt i))
    sp.co = new Curve25519Point[ringSize];
    for(int i=0; i<ringSize; i++) {
      sp.co[i] = inputCommitments[0][i];
      for(int j=1; j<inputs; j++) {
        sp.co[i] = sp.co[i].add(inputCommitments[j][i]);
      }
      for(int k=0; k<outputs.length; k++) {
        sp.co[i] = sp.co[i].subtract(outputs[k].co);
      }
    }

    // the public keys for every input referenced (including real inputs and decoys)
    sp.pk = new Curve25519PointPair[inputs][ringSize];

    // the secret key for every real input referenced
    sp.sk = new SK[inputs];

    // the key image for every real input referenced
    sp.ki = new Curve25519Point[inputs];

    for(int j=0; j<inputs; j++) {
      for(int i=0; i<ringSize; i++) {
        sp.pk[j][i] = (i==sp.iAsterisk) ? realInputs[j].pk : KEYGEN().pk;
      }
      sp.sk[j] = realInputs[j].sk;
      sp.ki[j] = realInputs[j].ki;
    }

    // the message being signed is a hash of the transaction, as defined in the C codebase as get_pre_mlsag_hash
    sp.M = fastHash(randomMessage(100));

    sp.s = Scalar.ZERO;
    for(int i=0; i<realInputs.length; i++) sp.s = sp.s.add(realInputs[i].mask);
    for(int i=0; i<outputs.length; i++) sp.s = sp.s.sub(outputs[i].mask);

    Curve25519Point S = realInputs[0].co;
    for(int i=1; i<realInputs.length; i++) S = S.add(realInputs[i].co);
    S = S.subtract(Curve25519Point.G.scalarMultiply(new Scalar(fee)));
    for(int i=0; i<outputs.length; i++) S = S.subtract(outputs[i].co);

    Curve25519Point S1 = getHpnGLookup(1).scalarMultiply(sp.s);

    if(!S.equals(S1)) throw new RuntimeException("S != S'");

    return sp;
  }

  public static void spendTest() {

    boolean pauseAtEachStage = false;
    int testIterations = 1;
    int decompositionBase = 2;
    int decompositionExponent = 8;
    int inputs = 2;

    System.out.println("Ring size: " + Math.pow(decompositionBase, decompositionExponent));
    System.out.println("Inputs: " + inputs);

    long startMs = new Date().getTime();
    SpendParams[] sp = new SpendParams[testIterations];
    for (int i=0; i<testIterations; i++) sp[i] = createTestSpendParams(decompositionBase, decompositionExponent, inputs);
    System.out.println("Spend params generation duration: " + (new Date().getTime()-startMs) + " ms");

    if(pauseAtEachStage) { System.out.println("Press enter to continue"); try { System.in.read(); } catch (Exception e) {}; System.out.println("Continuing..."); }

    Curve25519Point.scalarMults = 0;
    Curve25519Point.scalarBaseMults = 0;

    startMs = new Date().getTime();
    // create a transaction to spend the outputs, resulting in a signature that proves the authority to send them
    SpendSignature[] spendSignature = new SpendSignature[testIterations];
    for (int i=0; i<testIterations; i++) spendSignature[i] = SPEND(sp[i]);

    System.out.println("Spend signature generation duration: " + (new Date().getTime()-startMs) + " ms");

    byte[][] spendSignatureBytes = new byte[testIterations][];
    for (int i=0; i<testIterations; i++) {
      spendSignatureBytes[i] = spendSignature[i].toBytes();
      System.out.println("Spend Signature length (bytes):" + spendSignatureBytes[i].length);
    }

    if(pauseAtEachStage) { System.out.println("Press enter to continue"); try { System.in.read(); } catch (Exception e) {}; System.out.println("Continuing..."); }
    startMs = new Date().getTime();

    System.out.println("Spend ScalarMults: " + Curve25519Point.scalarMults);
    System.out.println("Spend BaseScalarMults: " + Curve25519Point.scalarBaseMults);
    Curve25519Point.scalarMults = 0;
    Curve25519Point.scalarBaseMults = 0;

    //Ed25519GroupElement.enableLineRecording = true;
    Curve25519Point.lineRecordingSourceFile = "StringCT.java";

    // verify the spend transaction
    for (int i=0; i<testIterations; i++) {

      //spendSignature[i] = SpendSignature.fromBytes(spendSignatureBytes[i]);

      boolean verified = VER(sp[i].ki, sp[i].pk, sp[i].co, spendSignature[i].co1, sp[i].M, spendSignature[i]);
      System.out.println("verified: " + verified);
    }

    System.out.println("Verify ScalarMults: " + Curve25519Point.scalarMults);
    System.out.println("Verify BaseScalarMults: " + Curve25519Point.scalarBaseMults);

    System.out.println("Signature verification duration: " + (new Date().getTime()-startMs) + " ms");

    if(Curve25519Point.enableLineRecording) Curve25519Point.lineNumberCallFrequencyMap.entrySet().stream().forEach(e->{System.out.println("line: " + e.getKey() + ", calls: " + e.getValue());});

  }

  public static void main(String[] args) {
    long startTime = new Date().getTime();
    spendTest();
    System.out.println("Total duration: " + (new Date().getTime()-startTime) + " ms");
  }

}
