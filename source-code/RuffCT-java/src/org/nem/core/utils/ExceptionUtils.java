package org.nem.core.utils;

import java.util.concurrent.*;
import java.util.function.Function;

/**
 * Static class that contains helper functions for dealing with exceptions.
 */
public class ExceptionUtils {

	private ExceptionUtils() {
	}

	/**
	 * Interface that mimics Runnable but can additionally throw checked exceptions.
	 */
	public interface CheckedRunnable {

		/**
		 * Executes the runnable.
		 *
		 * @throws Exception Any exception.
		 */
		void call() throws Exception;
	}

	/**
	 * Propagates checked exceptions as a runtime exception.
	 *
	 * @param runnable The checked runnable.
	 */
	public static void propagateVoid(final CheckedRunnable runnable) {
		propagateVoid(runnable, RuntimeException::new);
	}

	/**
	 * Propagates checked exceptions as a specific runtime exception.
	 *
	 * @param runnable The checked runnable.
	 * @param wrap A function that wraps an exception in a runtime exception.
	 * @param <E> The specific exception type.
	 */
	public static <E extends RuntimeException> void propagateVoid(
			final CheckedRunnable runnable,
			final Function<Exception, E> wrap) {
		propagate(new CheckedRuntimeToCallableAdapter(runnable), wrap);
	}

	/**
	 * Propagates checked exceptions as a runtime exception.
	 *
	 * @param callable The function.
	 * @param <T> The function return type.
	 * @return The function result.
	 */
	public static <T> T propagate(final Callable<T> callable) {
		return propagate(callable, RuntimeException::new);
	}

	/**
	 * Propagates checked exceptions as a specific runtime exception.
	 *
	 * @param callable The function.
	 * @param wrap A function that wraps an exception in a runtime exception.
	 * @param <T> The function return type.
	 * @param <E> The specific exception type.
	 * @return The function result.
	 */
	public static <T, E extends RuntimeException> T propagate(
			final Callable<T> callable,
			final Function<Exception, E> wrap) {
		try {
			return callable.call();
		} catch (final ExecutionException e) {
			if (RuntimeException.class.isAssignableFrom(e.getCause().getClass())) {
				throw (RuntimeException)e.getCause();
			}
			throw wrap.apply(e);
		} catch (final RuntimeException e) {
			throw e;
		} catch (final InterruptedException e) {
			Thread.currentThread().interrupt();
			throw new IllegalStateException(e);
		} catch (final Exception e) {
			throw wrap.apply(e);
		}
	}

	private static class CheckedRuntimeToCallableAdapter implements Callable<Void> {
		private final CheckedRunnable runnable;

		public CheckedRuntimeToCallableAdapter(final CheckedRunnable runnable) {
			this.runnable = runnable;
		}

		@Override
		public Void call() throws Exception {
			this.runnable.call();
			return null;
		}
	}
}
