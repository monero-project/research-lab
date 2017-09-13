package org.nem.core.utils;

import java.io.*;
import java.nio.channels.*;

/**
 * Static class that exposes functions for interacting with lock files.
 */
public class LockFile {

	/**
	 * Tries to acquire a file lock for the specified file.
	 *
	 * @param lockFile The lock file.
	 * @return A handle to the file lock if acquired, or null otherwise.
	 */
	public static Closeable tryAcquireLock(final File lockFile) {
		FileLockHandle handle = null;
		try {
			handle = new FileLockHandle(lockFile);

			// try to acquire the lock 5 times
			for (int i = 0; i < 5; ++i) {
				if (handle.tryLock()) {
					return handle;
				}

				ExceptionUtils.propagateVoid(() -> Thread.sleep(10));
			}

			return null;
		} catch (final IOException | OverlappingFileLockException e) {
			return null;
		} finally {
			if (null != handle && null == handle.lock) {
				try {
					handle.close();
				} catch (final IOException ignored) {
				}
			}
		}
	}

	/**
	 * Determines whether or not the specified file is locked.
	 *
	 * @param lockFile The lock file.
	 * @return true if the file is locked, false otherwise.
	 */
	public static boolean isLocked(final File lockFile) {
		try (final FileLockHandle handle = new FileLockHandle(lockFile)) {
			return !handle.tryLock();
		} catch (final OverlappingFileLockException e) {
			return true;
		} catch (final IOException e) {
			return false;
		}
	}

	private static class FileLockHandle implements Closeable {
		private final RandomAccessFile file;
		private FileLock lock;

		public FileLockHandle(final File lockFile) throws IOException {
			this.file = new RandomAccessFile(lockFile, "rw");
		}

		private boolean tryLock() throws IOException {
			this.lock = this.file.getChannel().tryLock();
			return null != this.lock;
		}

		@Override
		public void close() throws IOException {
			if (null != this.lock) {
				this.lock.close();
			}

			this.file.close();
		}
	}
}
