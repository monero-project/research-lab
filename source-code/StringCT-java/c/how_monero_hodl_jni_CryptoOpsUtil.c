#include "how_monero_hodl_jni_CryptoOpsUtil.h"
#include <unistd.h>
#include <stdint.h>
#include "crypto-ops.h"

JNIEXPORT jbyteArray JNICALL Java_how_monero_hodl_jni_CryptoOpsUtil_scalarMult
  (JNIEnv *env, jclass cls, jbyteArray pointBytes, jbyteArray scalarBytes) {

  jbyte* pointBytesBuf = (*env)->GetByteArrayElements(env, pointBytes, NULL);
  jbyte* scalarBytesBuf = (*env)->GetByteArrayElements(env, scalarBytes, NULL);

  ge_p3 pointp3;
  ge_p2 pointp2;
  ge_p2 pointp2result;

  ge_frombytes_vartime(&pointp3, (const unsigned char *) pointBytesBuf);

  ge_p3_to_p2(&pointp2, &pointp3);

  ge_scalarmult(&pointp2result, (const unsigned char *) scalarBytesBuf, &pointp3);

  unsigned char resultBytes[32];
  ge_tobytes(resultBytes, &pointp2result);
  

  jbyteArray returnData = (*env)->NewByteArray(env, 32);
  (*env)->SetByteArrayRegion(env, returnData, 0, 32, (jbyte *) resultBytes);

  return returnData;

}

//void ge_scalarmult_base(ge_p3 *h, const unsigned char *a) {
JNIEXPORT jbyteArray JNICALL Java_how_monero_hodl_jni_CryptoOpsUtil_scalarMultBase
  (JNIEnv *env, jclass cls, jbyteArray scalarBytes) {

  jbyte* scalarBytesBuf = (*env)->GetByteArrayElements(env, scalarBytes, NULL);

  ge_p3 pointp3result;
  ge_p2 pointp2result;

  ge_scalarmult_base(&pointp3result, (const unsigned char *) scalarBytesBuf);

  ge_p3_to_p2(&pointp2result, &pointp3result);

  unsigned char resultBytes[32];
  ge_tobytes(resultBytes, &pointp2result);


  jbyteArray returnData = (*env)->NewByteArray(env, 32);
  (*env)->SetByteArrayRegion(env, returnData, 0, 32, (jbyte *) resultBytes);

  return returnData;

}




//ge_double_scalarmult_base_vartime(ge_p2 *r, const unsigned char *a, const ge_p3 *A, const unsigned char *b)
//r = a * A + b * B
JNIEXPORT jbyteArray JNICALL Java_how_monero_hodl_jni_CryptoOpsUtil_doubleScalarMultBaseVartime
  (JNIEnv *env, jclass cls, jbyteArray aScalarBytes, jbyteArray pointBytes, jbyteArray bScalarBytes) {

  jbyte* pointBytesBuf = (*env)->GetByteArrayElements(env, pointBytes, NULL);
  jbyte* aScalarBytesBuf = (*env)->GetByteArrayElements(env, aScalarBytes, NULL);
  jbyte* bScalarBytesBuf = (*env)->GetByteArrayElements(env, bScalarBytes, NULL);

  ge_p3 pointp3;
  ge_p2 pointp2;
  ge_p2 pointp2result;

  ge_frombytes_vartime(&pointp3, (const unsigned char *) pointBytesBuf);

  ge_double_scalarmult_base_vartime(&pointp2result, (const unsigned char *) aScalarBytesBuf, &pointp3, (const unsigned char *) bScalarBytesBuf);

  unsigned char resultBytes[32];
  ge_tobytes(resultBytes, &pointp2result);


  jbyteArray returnData = (*env)->NewByteArray(env, 32);
  (*env)->SetByteArrayRegion(env, returnData, 0, 32, (jbyte *) resultBytes);

  return returnData;

}

