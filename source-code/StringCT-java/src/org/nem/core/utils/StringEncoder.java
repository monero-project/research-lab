package org.nem.core.utils;

import java.nio.charset.Charset;

/**
 * Static class that contains utility functions for converting strings to and from UTF-8 bytes.
 */
public class StringEncoder {

	private static final Charset ENCODING_CHARSET = Charset.forName("UTF-8");

	/**
	 * Converts a string to a UTF-8 byte array.
	 *
	 * @param s The input string.
	 * @return The output byte array.
	 */
	public static byte[] getBytes(final String s) {
		return s.getBytes(ENCODING_CHARSET);
	}

	/**
	 * Converts a UTF-8 byte array to a string.
	 *
	 * @param bytes The input byte array.
	 * @return The output string.
	 */
	public static String getString(final byte[] bytes) {
		return new String(bytes, ENCODING_CHARSET);
	}
}
