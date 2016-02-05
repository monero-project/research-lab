#see the aggregate schnorr pdf contained in this repository for an explanation. 
import MiniNero
import MLSAG
import LLW_Sigs
import PaperWallet
import Crypto.Random.random as rand
import binascii

b = 256
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493


def GenSchnorr(hash_prefix, pub, sec, k): 
    #modified from original algorithm to match Monero better
    #see the ag schnorr pdf for original alg.
    #Note in Monero, hash prefix is always 32 bytes..
    #hash_prefix = binascii.hexlify(prefix) 
    #k = PaperWallet.skGen() #comment for testing
    comm = MiniNero.scalarmultBase(k)
    print("comm", "hash_prefix", comm, hash_prefix)
    if MiniNero.scalarmultBase(sec) != pub:
        print"error in genSchnorr"
        return -1
    if MiniNero.sc_check(sec) == False:
        print "fail in geSchnorr"
        return -1
    c = MiniNero.sc_reduce_key(MiniNero.cn_fast_hash(hash_prefix + pub + comm))
    r = MiniNero.sc_sub_keys(k, MiniNero.sc_mul_keys(c, sec))
    #uncomment to test malleability
    c = MiniNero.sc_reduce_key(MiniNero.cn_fast_hash(hash_prefix + pub + comm))
    r = MiniNero.sc_unreduce_key(MiniNero.sc_sub_keys(k, MiniNero.sc_mul_keys(c, sec)))

    return r, c

def VerSchnorr(hash_prefix, pub, r, c):
    #hash_prefix = binascii.hexlify(prefix)
    check1 = MiniNero.toPoint(pub) 
    comm = MiniNero.addKeys(MiniNero.scalarmultKey(pub,c), MiniNero.scalarmultBase(r))
    c2 = MiniNero.cn_fast_hash(hash_prefix + pub + comm)
    print(MiniNero.sc_sub_keys(c, c2) == "0000000000000000000000000000000000000000000000000000000000000000")
    return (MiniNero.sc_sub_keys(c, c2) == "0000000000000000000000000000000000000000000000000000000000000000")

def GenSchnorrNonLinkable(x, P1, P2, index):
    if index == 0:
        a = PaperWallet.skGen()
        L1 = MiniNero.scalarmultBase(a)
        s2 = PaperWallet.skGen()
        c2 = MiniNero.cn_fast_hash(L1)
        L2 = MiniNero.addKeys(MiniNero.scalarmultBase(s2), MiniNero.scalarmultKey(P2, c2))
        c1 = MiniNero.cn_fast_hash(L2)
        s1 = MiniNero.sc_mulsub_keys(a,  x, c1)
    if index == 1:
        a = PaperWallet.skGen()
        L2 = MiniNero.scalarmultBase(a)
        s1 = PaperWallet.skGen()
        c1 = MiniNero.cn_fast_hash(L2)
        L1 = MiniNero.addKeys(MiniNero.scalarmultBase(s1), MiniNero.scalarmultKey(P1, c1))
        c2 = MiniNero.cn_fast_hash(L1)
        s2 = MiniNero.sc_mulsub_keys(a,  x, c2)
    return L1, s1, s2,

def VerSchnorrNonLinkable(P1, P2, L1, s1, s2):
    c2 = MiniNero.cn_fast_hash(L1)
    L2 = MiniNero.addKeys(MiniNero.scalarmultBase(s2), MiniNero.scalarmultKey(P2, c2))
    c1 = MiniNero.cn_fast_hash(L2)
    L1p = MiniNero.addKeys(MiniNero.scalarmultBase(s1), MiniNero.scalarmultKey(P1, c1))
    if L1 == L1p:
        print"Verified"
        return 0
    else:
        print "Didn't verify"
        print(L1,"!=",  L1p)
        return -1

    

def GenASNL(x, P1, P2, indices):
    #Aggregate Schnorr Non-Linkable
    #x, P1, P2, are key vectors here, but actually you 
    #indices specifices which column of the given row of the key vector you sign.
    #the key vector with the first or second key
    n = len(x)
    print("Generating Aggregate Schnorr Non-linkable Ring Signature")
    L1 = [None] * n
    s1 = [None] * n
    s2 = [None] * n
    s = MiniNero.intToHex(0)
    for j in range(0, n):
        L1[j], s1[j], s2[j] = GenSchnorrNonLinkable(x[j], P1[j], P2[j], indices[j])
        s = MiniNero.sc_add_keys(s, s1[j])
    return L1, s2, s
        
def VerASNL(P1, P2, L1, s2, s):
    #Aggregate Schnorr Non-Linkable
    print("Verifying Aggregate Schnorr Non-linkable Ring Signature")
    n = len(P1)
    LHS = MiniNero.scalarmultBase(MiniNero.intToHex(0))
    RHS = MiniNero.scalarmultBase(s)
    for j in range(0, n):
        c2 = MiniNero.cn_fast_hash(L1[j])
        L2 = MiniNero.addKeys(MiniNero.scalarmultBase(s2[j]), MiniNero.scalarmultKey(P2[j], c2))
        LHS = MiniNero.addKeys(LHS, L1[j])
        c1 = MiniNero.cn_fast_hash(L2)
        RHS = MiniNero.addKeys(RHS, MiniNero.scalarmultKey(P1[j], c1))
    if LHS == RHS:
        print"Verified"
        return 0
    else:
        print "Didn't verify"
        print(LHS,"!=",  RHS)
        return -1
        
