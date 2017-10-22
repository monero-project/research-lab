package test.how.monero.hodl;

import how.monero.hodl.crypto.Curve25519Point;
import how.monero.hodl.ringSignature.SpendParams;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import static how.monero.hodl.ringSignature.StringCT.*;
import static test.how.monero.hodl.StringCTSpendTest.createTestSpendParams;

public class StringCTBenchmarks {

  public static void spendTest() throws IOException {

    int[] inputsVariants = new int[]{1, 2, 3, 4, 5, 10, 20};
    int[] decompositionExponentVariants = new int[]{2, 3, 4, 5, 6, 7, 8, 9, 10};

    List<List<String>> sheet = new ArrayList<>();
    List<String> sheetColTitles = new ArrayList<>();
    sheetColTitles.add("Inputs");
    sheetColTitles.add("Base");
    sheetColTitles.add("Exponent");
    sheetColTitles.add("Ring size");
    sheetColTitles.add("Generation time (ms)");
    sheetColTitles.add("Generation scalar mults");
    sheetColTitles.add("Generation G scalar mults");
    sheetColTitles.add("Verification time (ms)");
    sheetColTitles.add("Verification scalar mults");
    sheetColTitles.add("Verification G scalar mults");
    sheetColTitles.add("Signature length excl. vins (bytes)");
    sheetColTitles.add("MLSAG equiv. length excl. vins (bytes)");
    sheet.add(sheetColTitles);

    int testIterations = 1;
    int decompositionBase = 2;

    for(int inputs : inputsVariants) {
      for(int decompositionExponent : decompositionExponentVariants) {

        System.out.println("******* inputs: " + inputs + ", decompositionExponent: " + decompositionExponent);

        long startMs = new Date().getTime();
        SpendParams[] sp = new SpendParams[testIterations];
        for (int i=0; i<testIterations; i++) sp[i] = createTestSpendParams(decompositionBase, decompositionExponent, inputs);
        long spendParamsGenerationDuration = (new Date().getTime()-startMs);
        System.out.println("Spend params generation duration: " + spendParamsGenerationDuration + " ms");

        startMs = new Date().getTime();
        // create a transaction to spend the outputs, resulting in a signature that proves the authority to send them
        SpendSignature[] spendSignature = new SpendSignature[testIterations];
        for (int i=0; i<testIterations; i++) {
          Curve25519Point.scalarMults = 0;
          Curve25519Point.scalarBaseMults = 0;
          spendSignature[i] = SPEND(sp[i]);
        }
        int spendScalarMults = Curve25519Point.scalarMults;
        int spendScalarBaseMults = Curve25519Point.scalarBaseMults;

        long spendSignatureGenerationDuration = (new Date().getTime()-startMs);
        System.out.println("Spend signature generation duration: " + spendSignatureGenerationDuration + " ms");

        byte[][] spendSignatureBytes = new byte[testIterations][];
        spendSignatureBytes[0] = spendSignature[0].toBytes();
        System.out.println("Spend Signature length (bytes):" + spendSignatureBytes[0].length);

        startMs = new Date().getTime();

        // verify the spend transaction
        for (int i=0; i<testIterations; i++) {
          Curve25519Point.scalarMults = 0;
          Curve25519Point.scalarBaseMults = 0;
          boolean verified = VER(sp[i].ki, sp[i].pk, sp[i].co, spendSignature[i].co1, sp[i].M, spendSignature[i]);
          System.out.println("verified: " + verified);
        }
        int verifyScalarMults = Curve25519Point.scalarMults;
        int verifyScalarBaseMults = Curve25519Point.scalarBaseMults;


        long spendSignatureVerificationDuration = (new Date().getTime()-startMs);
        System.out.println("Signature verification duration: " + spendSignatureVerificationDuration + " ms");


        List<String> sheetCols = new ArrayList<>();
        sheetCols.add(inputs+"");
        sheetCols.add(decompositionBase+"");
        sheetCols.add(decompositionExponent+"");
        sheetCols.add(((int)Math.pow(decompositionBase, decompositionExponent))+"");
        sheetCols.add((spendSignatureGenerationDuration/testIterations)+"");
        sheetCols.add((spendScalarMults)+"");
        sheetCols.add((spendScalarBaseMults)+"");
        sheetCols.add((spendSignatureVerificationDuration/testIterations)+"");
        sheetCols.add((verifyScalarMults)+"");
        sheetCols.add((verifyScalarBaseMults)+"");
        sheetCols.add((spendSignatureBytes[0].length)+"");
        sheetCols.add((inputs * (32 + 64 * ((int) Math.pow(decompositionBase, decompositionExponent))))+"");
        sheet.add(sheetCols);

      }
    }

    String csv = "";
    for(List<String> row : sheet) {
      for(int i=0; i<row.size(); i++) {
        csv+=row.get(i);
        if(i!=(row.size()-1)) csv+=",";
        else csv+="\n";
      }
    }
    System.out.println(csv);
    Files.write(new File(System.getProperty("user.home"), "stringCT-benchmarks.csv").toPath(), csv.getBytes());

  }


  public static void main(String[] args) throws Exception {
    long startTime = new Date().getTime();
    spendTest();
    System.out.println("\nTotal duration: " + (new Date().getTime()-startTime) + " ms");
  }

}
