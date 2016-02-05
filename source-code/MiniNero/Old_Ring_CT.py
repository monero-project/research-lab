#Work in progress obvously. This will implement the modified version of gmaxwells Confidential Transactions so that they work with ring signatures.
#The math is outlined in mrl_notes v4 (v3 is same but sign of z should be - in an equation) which can be found in this repository. 
import MiniNero
import LLW_Sigs
import PaperWallet

def getHForCT():
    A = MiniNero.publicFromInt(1)
    return MiniNero.hashToPoint_ct(A)

def binary(n):
    b = []
    while n:
        b = [n & 1] + b
        n >>= 1
    return b or [0]

def out_commitments(values):
    #do this first
    n = len(values)
    values2 = [None] * n
    for i in range(0, n):
        values2[i] = [MiniNero.intToHex(j) for j in binary(MiniNero.hexToInt(values[i]))]
    #returns a list of commitments C_i = y_iG + value_i * H for outputs (these masks are created randomly)
    masks = [None] * n 
    sumMasks = [None] * n
    for i in range(0, n):
        masks[i] = [PaperWallet.skGen() for jj in values2[i]] #binary decomposition for range proofs (could also use another base)
        sumMasks[i] = MiniNero.intToHex(sum([MiniNero.hexToInt(a) for a in masks[i]])) #sum is what actually goes into the ring..
    C = [None] * n
    for i in range(0, n):
        C[i] = MiniNero.addKeys(MiniNero.scalarmultBase(sumMasks[i]), MiniNero.scalarmultKey(H_ct, values[i]))
    return C, masks, sumMasks, values2

def in_commitments(input_value, sk, masks):
    #for now, assume there is one input, generalized after get that working
    sum_masks = MiniNero.intToHex(sum([MiniNero.hexToInt(a) for a in masks]))
    z = MiniNero.sc_sub_keys(sk, sum_masks) # z +  sum of input mask values = sk
    C = MiniNero.addKeys(MiniNero.scalarmultBase(sk), MiniNero.scalarmultKey(H_ct, input_value)) #input_value = sum output values
    return C, z #z is the sk you need to sign for this commitment

def CT_ring_sig(pk, C_in, C_out, xz, index):
    print("Generating Ct ring sig")
    n = len(pk)
    pk2 = [None] * 2
    for i in range(0, n):
        pk2[i] = MiniNero.addKeys(pk[i], C_in)
        for j in C_out:
            pk2[i] = MiniNero.subKeys(pk2[i], j)
    print("check validity", pk2[index], MiniNero.scalarmultBase(xz))
    if pk2[index] != MiniNero.scalarmultBase(xz):
        print("stop lying, you don't know a key")
        exit()
    I, c0, s = LLW_Sigs.LLW_Sig(pk2, xz, index)
    print("Ct ring sig generated")
    return I, c0, s, pk2

def rangeProof(C_out_i, masks_i):
    n = len(masks_i)
    I_Proofs = [None] * n
    c0s = [None] * n
    ss = [None] * n
    C_is = [None] * n
    for i in range(0, n):
        C_i = MiniNero.addKeys(MiniNero.scalarmultBase(masks_i[i]), MiniNero.scalarmultKey(H_ct, C_out_i[i])) # masks_i * G + C_out_i * H
        C_i_prime = MiniNero.subKeys(C_i, H_ct) #C_i - H
        C_is[i] = [C_i_prime, C_i]
        print("generating LLWsig for range proof from Cis, masks, couts", C_is[i], masks_i[i], C_out_i[i])
        I_Proofs[i], c0s[i], ss[i] = LLW_Sigs.LLW_Sig(C_is[i], masks_i[i], MiniNero.hexToInt(C_out_i[i]))
        #ring sig on the above, with sk masks_i
    return I_Proofs, c0s, ss, C_is

H_ct = getHForCT()
print("H", H_ct)

a = MiniNero.intToHex(49)
b1 = MiniNero.intToHex(30)
b2 = MiniNero.intToHex(20)
x_priv = PaperWallet.skGen() #our private key
x_commit = PaperWallet.skGen() # our private commitment key
#x_commit = x_priv #do with x_priv = x_commit first... , then modify by adding another mask
Pk1 = MiniNero.scalarmultBase(x_priv) #our public key
Pk2 = MiniNero.scalarmultBase(PaperWallet.skGen()) #other sk (we don't know it
print("xpriv, Pk1, Pk2", x_priv, Pk1, Pk2)

C_out, out_masks, sumMasks, values2 = out_commitments([b1, b2])

#testing rangeProofs
print("testing range proofs")
I_proofs, c0s, ss, Ci_s = rangeProof(values2[0], out_masks[0])
print("Iproofs, c0s, ss", I_proofs, c0s, ss)

print("C_out, outmasks", C_out, sumMasks)
C_in, z = in_commitments(a, x_commit, sumMasks)
print("C_in, z", C_in, z)
I, c0, s, PP = CT_ring_sig([Pk1, Pk2], C_in, C_out, MiniNero.sc_add_keys(x_priv,z), 0)
LLW_Sigs.LLW_Ver(PP, I, c0, s)
