package org.nem.core.utils;

/**
 * Wrapper that allows an object to be set once (or reset and set again).
 *
 * @param <T> The inner type.
 */
public class SetOnce<T> {
	private final T defaultValue;
	private T value;

	/**
	 * Creates a wrapper.
	 *
	 * @param defaultValue The default value.
	 */
	public SetOnce(final T defaultValue) {
		this.defaultValue = defaultValue;
	}

	/**
	 * Gets the inner object.
	 *
	 * @return The inner object.
	 */
	public T get() {
		return null == this.value ? this.defaultValue : this.value;
	}

	/**
	 * Sets the inner object.
	 *
	 * @param value The inner object.
	 */
	public void set(final T value) {
		if (null != this.value && null != value) {
			throw new IllegalStateException("cannot change value because it is already set");
		}

		this.value = value;
	}
}
