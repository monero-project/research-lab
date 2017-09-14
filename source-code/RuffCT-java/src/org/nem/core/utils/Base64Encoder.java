package org.nem.core.utils;

import org.apache.commons.codec.binary.Base64;

/**
 * Static class that contains utility functions for converting Base64 strings to and from bytes.
 */
public class Base64Encoder {

	/**
	 * Converts a string to a byte array.
	 *
	 * @param base64String The input Base64 string.
	 * @return The output byte array.
	 */
	public static byte[] getBytes(final String base64String) {
		final Base64 codec = new Base64();
		final byte[] encodedBytes = StringEncoder.getBytes(base64String);
		if (!codec.isInAlphabet(encodedBytes, true)) {
			throw new IllegalArgumentException("malformed base64 string passed to getBytes");
		}

		return codec.decode(encodedBytes);
	}

	/**
	 * Converts a byte array to a Base64 string.
	 *
	 * @param bytes The input byte array.
	 * @return The output Base64 string.
	 */
	public static String getString(final byte[] bytes) {
		final Base64 codec = new Base64();
		final byte[] decodedBytes = codec.encode(bytes);
		return StringEncoder.getString(decodedBytes);
	}
}
