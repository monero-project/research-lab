// Copyright (c) 2016, Monero Research Labs
//
// Author: Shen Noether <shen.noether@gmx.com>
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without modification, are
// permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice, this list of
//    conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright notice, this list
//    of conditions and the following disclaimer in the documentation and/or other
//    materials provided with the distribution.
//
// 3. Neither the name of the copyright holder nor the names of its contributors may be
//    used to endorse or promote products derived from this software without specific
//    prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
// EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
// MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
// THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
// STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
// THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#include "rctOps.h"
using namespace crypto;
using namespace std;

namespace rct {

    //Various key initialization functions

    //Creates a zero scalar
    void zero(key &zero) {
        int i = 0;
        for (i = 0; i < 32; i++) {
            zero[i] = (unsigned char)(0x00);
        }
    }

    //Creates a zero scalar
    key zero() {
        return{ {0x00, 0x00, 0x00,0x00 , 0x00, 0x00, 0x00,0x00 , 0x00, 0x00, 0x00,0x00 , 0x00, 0x00, 0x00,0x00 , 0x00, 0x00, 0x00,0x00 , 0x00, 0x00, 0x00,0x00 , 0x00, 0x00, 0x00,0x00 , 0x00, 0x00, 0x00,0x00  } };
    }

    //Creates a zero elliptic curve point
    void identity(key &Id) {
        int i = 0;
        Id[0] = (unsigned char)(0x01);
        for (i = 1; i < 32; i++) {
            Id[i] = (unsigned char)(0x00);
        }
    }

    //Creates a zero elliptic curve point
    key identity() {
        key Id;
        int i = 0;
        Id[0] = (unsigned char)(0x01);
        for (i = 1; i < 32; i++) {
            Id[i] = (unsigned char)(0x00);
        }
        return Id;
    }

    //copies a scalar or point
    void copy(key &AA, const key &A) {
        int i = 0;
        for (i = 0; i < 32; i++) {
            AA[i] = A[i];
        }
    }

    //copies a scalar or point
    key copy(const key &A) {
        int i = 0;
        key AA;
        for (i = 0; i < 32; i++) {
            AA[i] = A[i];
        }
        return AA;
    }


    //initializes a key matrix;
    //first parameter is rows,
    //second is columns
    keyM keyMInit(int rows, int cols) {
        keyM rv(cols);
        int i = 0;
        for (i = 0 ; i < cols ; i++) {
            rv[i] = keyV(rows);
        }
        return rv;
    }




    //Various key generation functions

    //generates a random scalar which can be used as a secret key or mask
    void skGen(key &sk) {
        unsigned char tmp[64];
        generate_random_bytes(64, tmp);
        sc_reduce(tmp);
        memcpy(sk.bytes, tmp, 32);
    }

    //generates a random scalar which can be used as a secret key or mask
    key skGen() {
        unsigned char tmp[64];
        generate_random_bytes(64, tmp);
        sc_reduce(tmp);
        key sk;
        memcpy(sk.bytes, tmp, 32);
        return sk;
    }

    //Generates a vector of secret key
    //Mainly used in testing
    keyV skvGen(int rows ) {
        keyV rv(rows);
        int i = 0;
        for (i = 0 ; i < rows ; i++) {
            skGen(rv[i]);
        }
        return rv;
    }

    //generates a random curve point (for testing)
    key  pkGen() {
        key sk = skGen();
        key pk = scalarmultBase(sk);
        return pk;
    }

    //generates a random secret and corresponding public key
    void skpkGen(key &sk, key &pk) {
        skGen(sk);
        scalarmultBase(pk, sk);
    }

    //generates a random secret and corresponding public key
    tuple<key, key>  skpkGen() {
        key sk = skGen();
        key pk = scalarmultBase(sk);
        return make_tuple(sk, pk);
    }

    //generates a <secret , public> / Pedersen commitment to the amount
    tuple<ctkey, ctkey> ctskpkGen(xmr_amount amount) {
        ctkey sk, pk;
        skpkGen(sk.dest, pk.dest);
        skpkGen(sk.mask, pk.mask);
        key am = d2h(amount);
        key aH = scalarmultH(am);
        addKeys(pk.mask, pk.mask, aH);
        return make_tuple(sk, pk);
    }
    
    
    //generates a <secret , public> / Pedersen commitment but takes bH as input 
    tuple<ctkey, ctkey> ctskpkGen(key bH) {
        ctkey sk, pk;
        skpkGen(sk.dest, pk.dest);
        skpkGen(sk.mask, pk.mask);
        //key am = d2h(amount);
        //key aH = scalarmultH(am);
        addKeys(pk.mask, pk.mask, bH);
        return make_tuple(sk, pk);
    }
    
    //generates a random uint long long
    xmr_amount randXmrAmount(xmr_amount upperlimit) {
        return h2d(skGen()) % (upperlimit);
    }

    //Scalar multiplications of curve points

    //does a * G where a is a scalar and G is the curve basepoint
    void scalarmultBase(key &aG,const key &a) {
        ge_p3 point;
        sc_reduce32copy(aG.bytes, a.bytes); //do this beforehand!
        ge_scalarmult_base(&point, aG.bytes);
        ge_p3_tobytes(aG.bytes, &point);
    }

    //does a * G where a is a scalar and G is the curve basepoint
    key scalarmultBase(const key & a) {
        ge_p3 point;
        key aG;
        sc_reduce32copy(aG.bytes, a.bytes); //do this beforehand
        ge_scalarmult_base(&point, aG.bytes);
        ge_p3_tobytes(aG.bytes, &point);
        return aG;
    }

    //does a * P where a is a scalar and P is an arbitrary point
    void scalarmultKey(key & aP, const key &P, const key &a) {
        ge_p3 A;
        ge_p2 R;
        ge_frombytes_vartime(&A, P.bytes);
        ge_scalarmult(&R, a.bytes, &A);
        ge_tobytes(aP.bytes, &R);
    }

    //does a * P where a is a scalar and P is an arbitrary point
    key scalarmultKey(const key & P, const key & a) {
        ge_p3 A;
        ge_p2 R;
        ge_frombytes_vartime(&A, P.bytes);
        ge_scalarmult(&R, a.bytes, &A);
        key aP;
        ge_tobytes(aP.bytes, &R);
        return aP;
    }


    //Computes aH where H= toPoint(cn_fast_hash(G)), G the basepoint
    key scalarmultH(const key & a) {
        ge_p3 A;
        ge_p2 R;
        key Htmp = { {0x8b, 0x65, 0x59, 0x70, 0x15, 0x37, 0x99, 0xaf, 0x2a, 0xea, 0xdc, 0x9f, 0xf1, 0xad, 0xd0, 0xea, 0x6c, 0x72, 0x51, 0xd5, 0x41, 0x54, 0xcf, 0xa9, 0x2c, 0x17, 0x3a, 0x0d, 0xd3, 0x9c, 0x1f, 0x94} };
        ge_frombytes_vartime(&A, Htmp.bytes);
        ge_scalarmult(&R, a.bytes, &A);
        key aP;
        ge_tobytes(aP.bytes, &R);
        return aP;
    }

    //Curve addition / subtractions

    //for curve points: AB = A + B
    void addKeys(key &AB, const key &A, const key &B) {
        ge_p3 B2, A2;
        ge_frombytes_vartime(&B2, B.bytes);
        ge_frombytes_vartime(&A2, A.bytes);
        ge_cached tmp2;
        ge_p3_to_cached(&tmp2, &B2);
        ge_p1p1 tmp3;
        ge_add(&tmp3, &A2, &tmp2);
        key rv;
        ge_p1p1_to_p3(&A2, &tmp3);
        ge_p3_tobytes(AB.bytes, &A2);
    }


    //addKeys1
    //aGB = aG + B where a is a scalar, G is the basepoint, and B is a point
    void addKeys1(key &aGB, const key &a, const key & B) {
        key aG = scalarmultBase(a);
        addKeys(aGB, aG, B);
    }

    //addKeys2
    //aGbB = aG + bB where a, b are scalars, G is the basepoint and B is a point
    void addKeys2(key &aGbB, const key &a, const key &b, const key & B) {
        ge_p2 rv;
        ge_p3 B2;
        ge_frombytes_vartime(&B2, B.bytes);
        ge_double_scalarmult_base_vartime(&rv, b.bytes, &B2, a.bytes);
        ge_tobytes(aGbB.bytes, &rv);
    }

    //Does some precomputation to make addKeys3 more efficient
    // input B a curve point and output a ge_dsmp which has precomputation applied
    void precomp(ge_dsmp rv, const key & B) {
        ge_p3 B2;
        ge_frombytes_vartime(&B2, B.bytes);
        ge_dsm_precomp(rv, &B2);
    }

    //addKeys3
    //aAbB = a*A + b*B where a, b are scalars, A, B are curve points
    //B must be input after applying "precomp"
    void addKeys3(key &aAbB, const key &a, const key &A, const key &b, const ge_dsmp B) {
        ge_p2 rv;
        ge_p3 A2;
        ge_frombytes_vartime(&A2, A.bytes);
        ge_double_scalarmult_precomp_vartime(&rv, a.bytes, &A2, b.bytes, B);
        ge_tobytes(aAbB.bytes, &rv);
    }


    //subtract Keys (subtracts curve points)
    //AB = A - B where A, B are curve points
    void subKeys(key & AB, const key &A, const key &B) {
        ge_p3 B2, A2;
        ge_frombytes_vartime(&B2, B.bytes);
        ge_frombytes_vartime(&A2, A.bytes);
        ge_cached tmp2;
        ge_p3_to_cached(&tmp2, &B2);
        ge_p1p1 tmp3;
        ge_sub(&tmp3, &A2, &tmp2);
        ge_p1p1_to_p3(&A2, &tmp3);
        ge_p3_tobytes(AB.bytes, &A2);
    }

    //checks if A, B are equal as curve points
    //without doing curve operations
    bool equalKeys(key & a, key & b) {
        key eqk;
        sc_sub(eqk.bytes, cn_fast_hash(a).bytes, cn_fast_hash(b).bytes);
        if (sc_isnonzero(eqk.bytes) ) {
            DP("eq bytes");
            DP(eqk);
            return false;
        }
        return true;
    }

    //Hashing - cn_fast_hash
    //be careful these are also in crypto namespace
    //cn_fast_hash for arbitrary multiples of 32 bytes
    void cn_fast_hash(key &hash, const void * data, const std::size_t l) {
        uint8_t md2[32];
        int j = 0;
        keccak((uint8_t *)data, l, md2, 32);
        for (j = 0; j < 32; j++) {
            hash[j] = (unsigned char)md2[j];
        }
        sc_reduce32(hash.bytes);
    }

    //cn_fast_hash for a 32 byte key
    void cn_fast_hash(key & hash, const key & in) {
        uint8_t md2[32];
        int j = 0;
        keccak((uint8_t *)in.bytes, 32, md2, 32);
        for (j = 0; j < 32; j++) {
            hash[j] = (unsigned char)md2[j];
        }
        sc_reduce32(hash.bytes);
    }

    //cn_fast_hash for a 32 byte key
    key cn_fast_hash(const key & in) {
        uint8_t md2[32];
        int j = 0;
        key hash;
        keccak((uint8_t *)in.bytes, 32, md2, 32);
        for (j = 0; j < 32; j++) {
            hash[j] = (unsigned char)md2[j];
        }
        sc_reduce32(hash.bytes);
        return hash;
    }

    //returns cn_fast_hash(input) * G where G is the basepoint
    key hashToPoint(const key & in) {
        return scalarmultBase(cn_fast_hash(in));
    }

    //returns cn_fast_hash(input) * G where G is the basepoint
    void hashToPoint(key & out, const key & in) {
        scalarmultBase(out, cn_fast_hash(in));
    }

    //sums a vector of curve points (for scalars use sc_add)
    void sumKeys(key & Csum, const keyV &  Cis) {
        identity(Csum);
        int i = 0;
        for (i = 0; i < Cis.size(); i++) {
            addKeys(Csum, Csum, Cis[i]);
        }
    }

    //Elliptic Curve Diffie Helman: encodes and decodes the amount b and mask a
    // where C= aG + bH
    void ecdhEncode(ecdhTuple & unmasked, const key & receiverPk) {
        key esk;
        //compute shared secret
        skpkGen(esk, unmasked.senderPk);
        key sharedSec1 = cn_fast_hash(scalarmultKey(receiverPk, esk));
        key sharedSec2 = cn_fast_hash(sharedSec1);
        //encode
        sc_add(unmasked.mask.bytes, unmasked.mask.bytes, sharedSec1.bytes);
        sc_add(unmasked.amount.bytes, unmasked.amount.bytes, sharedSec1.bytes);
    }
    void ecdhDecode(ecdhTuple & masked, const key & receiverSk) {
        //compute shared secret
        key sharedSec1 = cn_fast_hash(scalarmultKey(masked.senderPk, receiverSk));
        key sharedSec2 = cn_fast_hash(sharedSec1);
        //encode
        sc_sub(masked.mask.bytes, masked.mask.bytes, sharedSec1.bytes);
        sc_sub(masked.amount.bytes, masked.amount.bytes, sharedSec1.bytes);
    }
}
