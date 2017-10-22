package how.monero.hodl.cursor;

import how.monero.hodl.crypto.Curve25519Point;
import how.monero.hodl.crypto.Curve25519PointPair;
import how.monero.hodl.crypto.Scalar;

public class StringCTCursor extends Cursor {
  public byte[] data;

  public StringCTCursor(byte[] data) {
    super(data);
  }

  public Curve25519Point readGroupElement() {
    return new Curve25519Point(readBytes(32));
  }
  public Curve25519PointPair[] readPointPairArray(int len) {
    Curve25519PointPair[] result = new Curve25519PointPair[len];
    for(int i=0; i<len; i++) result[i] = new Curve25519PointPair(readGroupElement(), readGroupElement());
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
