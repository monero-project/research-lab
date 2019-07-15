package org.nem.core.utils;


import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import org.junit.Test;

public class ArrayUtilsTest {

  @Test
  public void duplicate() {

    // Arrange
    byte[] bytes = "test".getBytes(StandardCharsets.UTF_8);
    int bytesHash = Arrays.hashCode(bytes);

    // Act
    byte[] duplicate = ArrayUtils.duplicate(bytes);

    // Assert: original array is unchanged
    assertEquals(bytesHash, Arrays.hashCode(bytes));

    // Assert: check duplicate
    assertArrayEquals(bytes, duplicate);
  }
}
