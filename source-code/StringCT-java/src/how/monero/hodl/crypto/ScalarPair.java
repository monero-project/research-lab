package how.monero.hodl.crypto;

import org.nem.core.crypto.ed25519.arithmetic.Ed25519FieldElement;

public class ScalarPair {
    Ed25519FieldElement p1;
    Ed25519FieldElement p2;
    public ScalarPair(Ed25519FieldElement p1, Ed25519FieldElement p2) {
      this.p1 = p1;
      this.p2 = p2;
    }
  }
