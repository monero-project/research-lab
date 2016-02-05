#see https://eprint.iacr.org/2015/1098.pdf
#this one is same as MLSAG.py, I'm just experimenting with 
#how to best implement it..
import MiniNero
import PaperWallet

def keyVector(rows):
    return [None] * rows

def keyMatrix(rows, cols):
    #first index is columns (so slightly backward from math)
    rv = [None] * cols
    for i in range(0, cols):
        rv[i] = keyVector(rows)
    return rv

def hashKeyVector(v):
    return [MiniNero.hashToPoint_cn(vi) for vi in v]

def vScalarMultBase(v):
    return [MiniNero.scalarmultBase(a) for a in v]

def keyImageV(x):
    #takes as input a keyvector, returns the keyimage-vector
    return [MiniNero.scalarmultKey(MiniNero.hashToPoint_cn(MiniNero.scalarmultBase(xx)), xx) for xx in x]

def skvGen(n):
    return [PaperWallet.skGen() for i in range(0, n)] 

def skmGen(r, c):
    rv = keyMatrix(r, c)
    for i in range(0, c):
        rv[i] = skvGen(r)
    return rv

def MLSAG_Gen(pk, xx, index ):
    rows = len(xx)
    cols = len(pk)
    print("Generating MG sig of size ", rows, "x", cols)
    print("index is:", index)
    print("checking if I can actually sign")
    print(pk[index])
    print([MiniNero.scalarmultBase(x) for x in xx])
    c= [None] * cols
    alpha = skvGen(rows)
    I = keyImageV(xx)
    L = keyMatrix(rows, cols)
    R = keyMatrix(rows, cols)
    s = keyMatrix(rows, cols)
    m = ''.join(pk[0])
    for i in range(1, cols):
        m = m + ''.join(pk[i])
    L[index] = [MiniNero.scalarmultBase(aa) for aa in alpha] #L = aG
    Hi = hashKeyVector(pk[index])
    R[index] = [MiniNero.scalarmultKey(Hi[ii], alpha[ii]) for ii in range(0, rows)] #R = aI
    oldi = index
    i = (index + 1) % cols
    c[i] = MiniNero.cn_fast_hash(m+''.join(L[oldi]) + ''.join(R[oldi]))
    
    while i != index:
        s[i] = skvGen(rows)
        L[i] = [MiniNero.addKeys1(s[i][j], c[i], pk[i][j]) for j in range(0, rows)]

        Hi = hashKeyVector(pk[i])
        R[i] = [MiniNero.addKeys2( s[i][j], Hi[j], c[i], I[j]) for j in range(0, rows)]
        oldi = i
        i = (i + 1) % cols
        c[i] = MiniNero.cn_fast_hash(m+''.join(L[oldi]) + ''.join(R[oldi]))
    print("L", L)
    print("R", R)
    s[index] = [MiniNero.sc_mulsub_keys(alpha[j], c[index], xx[j]) for j in range(0, rows)] #alpha - c * x
    return I, c[0], s

def MLSAG_Ver(pk, I, c0, s ):
    rows = len(pk[0])
    cols = len(pk)
    print("verifying MG sig of dimensions ",rows ,"x ", cols)
    c= [None] * (cols + 1)
    c[0] = c0
    L = keyMatrix(rows, cols)
    R = keyMatrix(rows, cols)
    m = ''.join(pk[0])
    for i in range(1, cols):
        m = m + ''.join(pk[i])
    i = 0
    while i < cols:
        L[i] = [MiniNero.addKeys1(s[i][j], c[i], pk[i][j]) for j in range(0, rows)]

        Hi = hashKeyVector(pk[i])
        R[i] = [MiniNero.addKeys2( s[i][j], Hi[j], c[i], I[j]) for j in range(0, rows)]

        oldi = i
        i = i + 1
        c[i] = MiniNero.cn_fast_hash(m+''.join(L[oldi]) + ''.join(R[oldi]))
    print("L", L)
    print("R", R) 
    print("c", c)

    return (c0 == c[cols])

