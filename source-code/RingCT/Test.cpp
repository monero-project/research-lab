#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <tuple>
#include <limits>
#include <cstddef>
#include <iostream>
#include "crypto-ops.h"
#include "crypto.h"
#include "keccak.h"

#define DBG

#include "rctTypes.h"
#include "rctOps.h"
#include "rctSigs.h"

#define BYTES 64
using namespace crypto;
using namespace std;
using namespace rct;


int main(int argc, char *argv[]) {
    DP("Running tests for ASNL, MG sigs, and Ring CT");




    //Schnorr NonLinkable true one and false one
    DP("Schnorr non-linkable tests");
    //x, P1 = PaperWallet.skpkGen()
    key x, P1;
    skpkGen(x, P1);

    key P2 = pkGen();
    key P3 = pkGen();

    //L1, s1, s2 = ASNL.GenSchnorrNonLinkable(x, P1, P2, 0)
    key L1, s1, s2;
    GenSchnorrNonLinkable(L1, s1, s2, x, P1, P2, 0);

    DP("This one should verify!");
    DP(VerSchnorrNonLinkable(P1, P2, L1, s1, s2));
    DP("");
    DP("This one should NOT verify!");
    DP(VerSchnorrNonLinkable(P1, P3, L1, s1, s2));


    //Tests for ASNL
    //#ASNL true one, false one, C != sum Ci, and one out of the range..

    DP("\n\n ASNL tests");
    int N = 64;
    key64 xv;
    key64 P1v;
    key64 P2v;
    bits indi;
    
    int j = 0;
    for (j = 0 ; j < N ; j++) {
        indi[j] = (int)randXmrAmount(1);
        xv[j] = skGen();
        if ( indi[j] == 0 ) {
            P1v[j] = scalarmultBase(xv[j]);
            P2v[j] = pkGen();
        } else {
            P2v[j] = scalarmultBase(xv[j]);
            P1v[j] = pkGen();
        }
    }
    
    asnlSig L1s2s = GenASNL(xv, P1v, P2v, indi);
    //#true one
    DP("This one should verify!");

    DP(VerASNL(P1v, P2v, L1s2s));
    //#false one
    indi[3] = (indi[3] + 1) % 2;
    DP("");
    DP("This one should NOT verify!");
    L1s2s = GenASNL(xv, P1v, P2v, indi);
    DP(VerASNL(P1v, P2v, L1s2s));

    DP("\n\nMG sig tests");

    //Tests for MG Sigs
    //#MG sig: true one
    N = 3;// #cols
    int   R = 3;// #rows
    keyV xtmp = skvGen(R);
    keyM xm = keyMInit(R, N);// = [[None]*N] #just used to generate test public keys
    keyV sk = skvGen(R);
    keyM P  = keyMInit(R, N);// = keyM[[None]*N] #stores the public keys;
    DP("MG Sig: this one should verify!"); 
    int ind = 2;
    int i = 0;
    for (j = 0 ; j < R ; j++) {
        for (i = 0 ; i < N ; i++)
        {
            xm[i][j] = skGen();
            P[i][j] = scalarmultBase(xm[i][j]);
        }
    }
    for (j = 0 ; j < R ; j++) {
        sk[j] = xm[ind][j];
    }
    mgSig IIccss = MLSAG_Gen(P, sk, ind);
    DP("Sig verified?");
    DP(MLSAG_Ver(P, IIccss) );

    //#MG sig: false one
    DP("MG Sig: this one should NOT verify!");
    N = 3;// #cols
    R = 3;// #rows
    xtmp = skvGen(R);
    keyM xx(N, xtmp);// = [[None]*N] #just used to generate test public keys
    sk = skvGen(R);
    //P (N, xtmp);// = keyM[[None]*N] #stores the public keys;

    ind = 2;
    for (j = 0 ; j < R ; j++) {
        for (i = 0 ; i < N ; i++)
        {
            xx[i][j] = skGen();
            P[i][j] = scalarmultBase(xx[i][j]);
        }
        sk[j] = xx[ind][j];
    }
    sk[2] = skGen();//asume we don't know one of the private keys..
    IIccss = MLSAG_Gen(P, sk, ind);
    DP("Sig verified?");
    DP(MLSAG_Ver(P, IIccss) );
    
    
    
    //Ring CT Stuff
    //ct range proofs
    DP("\n\n Ring CT tests");
    DP("Everything below should verify!");
    ctkeyV sc, pc;
    ctkey sctmp, pctmp;
    //add fake input 5000
    tie(sctmp, pctmp) = ctskpkGen(6000);
    sc.push_back(sctmp);
    pc.push_back(pctmp);


    tie(sctmp, pctmp) = ctskpkGen(7000);
    sc.push_back(sctmp);
    pc.push_back(pctmp);
    vector<xmr_amount >amounts;


    //add output 500
    amounts.push_back(500);
    keyV destinations;
    key Sk, Pk;
    skpkGen(Sk, Pk);
    destinations.push_back(Pk);


    //add output for 12500
    amounts.push_back(12500);
    skpkGen(Sk, Pk);
    destinations.push_back(Pk);

    //compute rct data with mixin 500
    DP("computing ring ct sig with mixin 500");
    rctSig s = genRct(sc, pc, destinations, amounts, 500);

    //verify rct data
    DP("test sig verifies?");
    DP(verRct(s));

    //decode received amount
    DP("decode amounts working?");
    DP(decodeRct(s, Sk, 1));
    
    
    
    
    
    
    DP("\nRing CT with failing MG sig part should not verify!");
    DP("Since sum of inputs != outputs");
        
    amounts[1] = 12501;
    skpkGen(Sk, Pk);
    destinations[1] = Pk;
    
    
    //compute rct data with mixin 500
    s = genRct(sc, pc, destinations, amounts, 500);

    //verify rct data
    DP("test sig verifies?");
    DP(verRct(s));

    //decode received amount
    DP("decode amounts working?");
    DP(decodeRct(s, Sk, 1));    
    
    
         
         
         return 0;
}
