package org.nem.core.utils;

import org.apache.commons.codec.DecoderException;
import org.apache.commons.codec.binary.Hex;

/**
 * Static class that contains utility functions for converting hex strings to and from bytes.
 */
public class HexEncoder {

	/**
	 * Converts a hex string to a byte array.
	 *
	 * @param hexString The input hex string.
	 * @return The output byte array.
	 */
	public static byte[] getBytes(final String hexString) {
		try {
			return getBytesInternal(hexString);
		} catch (final DecoderException e) {
			throw new IllegalArgumentException(e);
		}
	}

	/**
	 * Tries to convert a hex string to a byte array.
	 *
	 * @param hexString The input hex string.
	 * @return The output byte array or null if the input string is malformed.
	 */
	public static byte[] tryGetBytes(final String hexString) {
		try {
			return getBytesInternal(hexString);
		} catch (final DecoderException e) {
			return null;
		}
	}

	private static byte[] getBytesInternal(final String hexString) throws DecoderException {
		final Hex codec = new Hex();
		final String paddedHexString = 0 == hexString.length() % 2 ? hexString : "0" + hexString;
		final byte[] encodedBytes = StringEncoder.getBytes(paddedHexString);
		return codec.decode(encodedBytes);
	}

	/**
	 * Converts a byte array to a hex string.
	 *
	 * @param bytes The input byte array.
	 * @return The output hex string.
	 */
	public static String getString(final byte[] bytes) {
		final Hex codec = new Hex();
		final byte[] decodedBytes = codec.encode(bytes);
		return StringEncoder.getString(decodedBytes);
	}
}
