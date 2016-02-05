#see mrl_notes .. obv this is a work in progress
import MiniNero
import PaperWallet

def keyImage(x):
    HP = MiniNero.hashToPoint_ct(MiniNero.scalarmultBase(x))
    return MiniNero.scalarmultKey(HP, x)

def LLW_Sig(pk, xx, index ):
    n = len(pk)
    print("Generating LLW sig of length ", n)
    L = [None] * n
    R = [None] * n
    c= [None] * n
    s = [PaperWallet.skGen() for i in range(0, n)] 
    HP = [MiniNero.hashToPoint_ct(i) for i in pk]
    pj = ''.join(pk)
    keyimage = keyImage(xx) #ok
    s[index] = MiniNero.mul_8(s[index])
    L[index] = MiniNero.scalarmultBase(s[index])
    R[index] = MiniNero.scalarmultKey(HP[index], s[index]) #aH
    j = (index + 1) % n
    c[j] = MiniNero.cn_fast_hash(pj+L[index]+R[index])
    while j != index:
        L[j] = MiniNero.addKeys(MiniNero.scalarmultBase(s[j]), MiniNero.scalarmultKey(pk[j], c[j])) #Lj = sG + cxG
        R[j] = MiniNero.addKeys(MiniNero.scalarmultKey(HP[j], s[j]), MiniNero.scalarmultKey(keyimage, c[j])) #Rj = sH + cxH
        cj = (j + 1) % n
        c[cj] = MiniNero.cn_fast_hash(pj + L[j] + R[j]) #c j+1 = H(pk + Lj + Rj
        j = cj #increment j
    s[index] = MiniNero.sc_mulsub_keys(s[index], c[index], xx) #si = a - c x so a = s + c x
    print("sigma = ", keyimage, c[0], s[:])
    return keyimage, c[0], s[:]

def LLW_Ver(pk, keyimage, c1, s):
    n= len(pk) #ok
    print("verifying LLW sig of length", n)
    L = [None]*n
    R = [None]*n
    c= [None]*(n+1)
    pj = ''.join(pk)
    HP = [MiniNero.hashToPoint_ct(i) for i in pk]
    c[0] = c1
    j = 0
    while j < n:
        L[j] = MiniNero.addKeys(MiniNero.scalarmultBase(s[j]), MiniNero.scalarmultKey(pk[j], c[j]))
        R[j] = MiniNero.addKeys(MiniNero.scalarmultKey(HP[j], s[j]), MiniNero.scalarmultKey(keyimage, c[j]))
        cj = j + 1
        c[cj] = MiniNero.cn_fast_hash(pj + L[j] + R[j])
        j = cj
    rv = (c[0] == c[n])
    print("sig verifies complete", rv)
    print("c", c)
    print("L", L)
    print("R", R)
    return rv
