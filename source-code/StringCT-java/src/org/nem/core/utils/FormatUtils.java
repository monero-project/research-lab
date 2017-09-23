package org.nem.core.utils;

import java.text.*;
import java.util.Arrays;

/**
 * Static class containing helper functions for formatting.
 */
public class FormatUtils {

	/**
	 * Gets a default decimal format that should be used for formatting decimal values.
	 *
	 * @return A default decimal format.
	 */
	public static DecimalFormat getDefaultDecimalFormat() {
		final DecimalFormatSymbols decimalFormatSymbols = new DecimalFormatSymbols();
		decimalFormatSymbols.setDecimalSeparator('.');
		final DecimalFormat format = new DecimalFormat("#0.000", decimalFormatSymbols);
		format.setGroupingUsed(false);
		return format;
	}

	/**
	 * Gets a decimal format that with the desired number of decimal places.
	 *
	 * @param decimalPlaces The number of decimal places.
	 * @return The desired decimal format.
	 */
	public static DecimalFormat getDecimalFormat(final int decimalPlaces) {
		if (decimalPlaces < 0) {
			throw new IllegalArgumentException("decimalPlaces must be non-negative");
		}

		final DecimalFormatSymbols decimalFormatSymbols = new DecimalFormatSymbols();
		decimalFormatSymbols.setDecimalSeparator('.');
		final StringBuilder builder = new StringBuilder();
		builder.append("#0");

		if (decimalPlaces > 0) {
			builder.append('.');
			final char[] zeros = new char[decimalPlaces];
			Arrays.fill(zeros, '0');
			builder.append(zeros);
		}

		final DecimalFormat format = new DecimalFormat(builder.toString(), decimalFormatSymbols);
		format.setGroupingUsed(false);
		return format;
	}

	/**
	 * Formats a double value with a given number of decimal places.
	 *
	 * @param value The value to format.
	 * @param decimalPlaces The desired number of decimal places.
	 * @return The formatted string.
	 */
	public static String format(final double value, final int decimalPlaces) {
		final DecimalFormat formatter = getDecimalFormat(decimalPlaces);
		return formatter.format(value);
	}
}
