#!/usr/bin/python
import sys #for arguments
import MiniNero
import mnemonic
import PaperWallet
import Ecdh
import ASNL
import MLSAG
import MLSAG2
import LLW_Sigs
import RingCT
import Crypto.Random.random as rand
import Translator
import binascii
import RingCT2

#Schnorr NonLinkable true one and false one
x, P1 = PaperWallet.skpkGen()
P2 = PaperWallet.pkGen()
P3 = PaperWallet.pkGen()

L1, s1, s2 = ASNL.GenSchnorrNonLinkable(x, P1, P2, 0)

print("Testing Schnorr Non-linkable!")
print("This one should verify!")
print(ASNL.VerSchnorrNonLinkable(P1, P2, L1, s1, s2))
print("")
print("This one should NOT verify!")
print(ASNL.VerSchnorrNonLinkable(P1, P3, L1, s1, s2))

#ASNL true one, false one, C != sum Ci, and one out of the range..

print("\n\n\nTesting ASNL")
N = 10
x = [None] * N
P1 = [None] * N
P2 = [None] * N
indi = [None] * N
for j in range(0, N):
    indi[j] = rand.getrandbits(1)
    x[j] = PaperWallet.skGen()
    if indi[j] == 0:
        P1[j] = MiniNero.scalarmultBase(x[j])
        P2[j] = PaperWallet.pkGen()
    else:
        P2[j] = MiniNero.scalarmultBase(x[j])
        P1[j] = PaperWallet.pkGen()
L1, s2, s = ASNL.GenASNL(x, P1, P2, indi)
#true one
print("This one should verify!")

ASNL.VerASNL(P1, P2, L1, s2, s)
#false one 
indi[3] = (indi[3] + 1) % 2
print("")
print("This one should NOT verify!")
L1, s2, s = ASNL.GenASNL(x, P1, P2, indi)
ASNL.VerASNL(P1, P2, L1, s2, s)

#MG sig: true one 
print("\n\n\nTesting MG Sig: this one should verify!")
N = 3 #cols
R = 3 #rows
x = [None] * N #just used to generate test public keys
sk = [None]* R #vector of secret keys
P = [None]*N #stores the public keys

ind = 2
for j in range(0, N):
    x[j] = [None] * R
    P[j] = [None] * R
    for i in range(0, R):
        x[j][i] = PaperWallet.skGen()
        P[j][i] = MiniNero.scalarmultBase(x[j][i])
for j in range(0, R):
    sk[j] = x[j][ind]

print("x", x)
II, cc, ss = MLSAG.MLSAG_Sign(P, sk, ind) 
print("Sig verified?", MLSAG.MLSAG_Ver(P, II, cc, ss) )


#MG sig: false one
print("\n\nMG Sig: this one should NOT verify!")
N = 3 #cols
R = 3 #rows
x = [None]*N #just used to generate test public keys
sk = [None] * R #vector of secret keys
P = [None]*N #stores the public keys
ind = 2
for j in range(0, N):
    x[j] = [None] * R
    P[j] = [None] * R
    for i in range(0, R):
        x[j][i] = PaperWallet.skGen()
        P[j][i] = MiniNero.scalarmultBase(x[j][i])

for j in range(0, R):
    sk[j] = x[j][ind]
sk[2] = PaperWallet.skGen() #assume we don't know one of the secret keys
print("x", x)
II, cc, ss = MLSAG.MLSAG_Sign(P, sk, ind) 
print("Sig verified?", MLSAG.MLSAG_Ver(P, II, cc, ss) )


#rct Sig:  range proof true / false, sum Ci true / false, MG sig true / false, 


print("\n\n\nTesting Ring CT")

sc = []
pc = []

sctmp, pctmp = RingCT2.ctskpkGen(60)
sc.append(sctmp)
pc.append(pctmp)

sctmp, pctmp = RingCT2.ctskpkGen(70)
sc.append(sctmp)
pc.append(pctmp)

#add output 500
amounts = []
amounts.append(5)
destinations = []
Sk, Pk = PaperWallet.skpkGen()
destinations.append(Pk)

#add output for 12500
amounts.append(125);
Sk, Pk = PaperWallet.skpkGen()
destinations.append(Pk)

s = RingCT2.genRct(sc, pc, destinations, amounts, 2)

print("attempting to verify")
print(RingCT2.verRct(s))

#decode received amount
print("decode amounts working?")
print(RingCT2.decodeRct(s, Sk, 0))
print("decode amounts working?")
print(RingCT2.decodeRct(s, Sk, 1))
