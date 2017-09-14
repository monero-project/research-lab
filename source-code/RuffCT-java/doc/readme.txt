Instructions for compiling the Ed25519 native library
-----------------------------------------------------

Note: You don't need to do any of this if you don't want to. The code will automatically fall back to a pure Java Ed25519 implementation.


To compile the JNI C library:

cd <path to RuffCT-java/c directory>

# replace <OS> with darwin on OSX, or with linux on Linux.
gcc -fPIC -c how_monero_hodl_jni_CryptoOpsUtil.c crypto-ops.c crypto-ops-data.c -I /<path to jdk>/include/<OS>/ -I /<path to jdk>/include

gcc -dynamiclib -o libcryptoopsutil.jnilib how_monero_hodl_jni_CryptoOpsUtil.o crypto-ops.o crypto-ops-data.o -framework JavaVM

When running Java code that uses this JNI library, provide the following command line argument:

-Djava.library.path=/<path to directory containing libcryptoopsutil.jnilib>

