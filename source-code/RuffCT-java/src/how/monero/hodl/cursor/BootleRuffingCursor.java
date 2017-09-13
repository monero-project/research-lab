package how.monero.hodl.cursor;

import how.monero.hodl.crypto.PointPair;
import how.monero.hodl.crypto.Scalar;
import org.nem.core.crypto.ed25519.arithmetic.Ed25519EncodedFieldElement;
import org.nem.core.crypto.ed25519.arithmetic.Ed25519EncodedGroupElement;
import org.nem.core.crypto.ed25519.arithmetic.Ed25519FieldElement;
import org.nem.core.crypto.ed25519.arithmetic.Ed25519GroupElement;

public class BootleRuffingCursor extends Cursor {
  public byte[] data;

  public BootleRuffingCursor(byte[] data) {
    super(data);
  }

  public Ed25519GroupElement readGroupElement() {
    return new Ed25519EncodedGroupElement(readBytes(32)).decode();
  }
  public Ed25519FieldElement readFieldElement() {
    return new Ed25519EncodedFieldElement(readBytes(32)).decode();
  }
  public PointPair[] readPointPairArray(int len) {
    PointPair[] result = new PointPair[len];
    for(int i=0; i<len; i++) result[i] = new PointPair(readGroupElement(), readGroupElement());
    return result;
  }
  public Scalar[][] readScalar2DArray(int m, int n) {
    Scalar[][] result = new Scalar[m][n];
    for(int j=0; j<m; j++) {
      for(int i=0; i<n; i++) {
        result[j][i] = readScalar();
      }
    }
    return result;
  }

}
