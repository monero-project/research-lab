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

#include "rctMSig.h"
using namespace crypto;
using namespace std;

namespace rct {
    
    int i;
    //Generate Signing Keys 
    //This function is called by each participant in 
    //A ring multisignature transaction. 
    //The participant will send the returned parameters 
    //to whomever is managing the transaction. 
    //returns a, aG, aHP and I 
    tuple<key, key, key, key> InitiateRMS(key x) {
        key I = scalarmultKey(hashToPoint(scalarmultBase(x)), x);
        key a, aG;
        skpkGen(a, aG);
        key aHP = scalarmultKey(hashToPoint(scalarmultBase(x)), a);
        return make_tuple(a, aG, aHP, I);
    }
    
    //returns "c" which is the last index needed to get the last s-values
    key rmsMgSigStart(const keyM & pk, mgSig & rv, keyV aG, keyV aHP, const int index) {

		int rows = pk[0].size();
		int cols = pk.size();
		if (cols < 2) {
			printf("Error! What is c if cols = 1!");
		}
		int i = 0, j = 0;
		key c, c_old, c0, L, R, Hi;
        sc_0(c_old.bytes);
		vector<ge_dsmp> Ip(rows);
		rv.ss = keyM(cols, rv.II);
        unsigned char m2[96]; 
		for (i = 0; i < rows; i++) {
            memcpy(m2, pk[index][i].bytes, 32);
            memcpy(m2 + 32, aG[i].bytes, 32);
            memcpy(m2 + 64, aHP[i].bytes, 32);
			precomp(Ip[i], rv.II[i]);
            sc_add(c_old.bytes, c_old.bytes, cn_fast_hash96(m2).bytes);
		}

		int oldi = index;
		i = (index + 1) % cols;
		while (i != index) {

			rv.ss[i] = skvGen(rows);            
            sc_0(c.bytes);
			for (j = 0; j < rows; j++) {
				addKeys2(L, rv.ss[i][j], c_old, pk[i][j]);
				hashToPoint(Hi, pk[i][j]);
				addKeys3(R, rv.ss[i][j], Hi, c_old, Ip[j]);
                memcpy(m2, pk[i][j].bytes, 32);
                memcpy(m2 + 32, L.bytes, 32);
                memcpy(m2 + 64, R.bytes, 32);      
                sc_add(c.bytes, c.bytes, cn_fast_hash96(m2).bytes);
			}
            c_old = copy(c);
            if (i == 0) { 
                c0 = copy(c);
			}
			oldi = i;
			i = (i + 1) % cols;
		}
		return c;
	}
    
    //have to return s = a - cx
    //for each participant in the MG sig..
    key rmsSign(key a, key c, key x) {
        key s;
        sc_mulsub(s.bytes, c.bytes, x.bytes, a.bytes);
        return s;
    }
        
}