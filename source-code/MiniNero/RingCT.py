import MiniNero
import MLSAG
import LLW_Sigs
import PaperWallet
import AggregateSchnorr
import Ecdh
import Translator

def getHForCT():
    return "8b655970153799af2aeadc9ff1add0ea6c7251d54154cfa92c173a0dd39c1f94"
    A = MiniNero.publicFromInt(1)
    H = MiniNero.hashToPoint_ct(A)
    Translator.hexToC(H) 
    print(H)
    return H
    
def getH2ForCT():
    A = MiniNero.publicFromInt(1)
    HPow2 = MiniNero.hashToPoint_ct(A)
    two = MiniNero.intToHex(2)
    H2 = [None] * 64
    for i in range(0, 64):
        Translator.hexToCComma(HPow2) 
        H2[i] = HPow2
        HPow2 = MiniNero.scalarmultKey(HPow2, two)
    return H2
    
def binary(n, digits):
    b = [0] * digits
    i = 0
    while n:
        b[i] = n & 1
        i = i + 1
        n >>= 1
    return b 

#unused? (Maybe I was just using for testing..)
def dec(binArray):
    s = 0
    i = 0
    for a in binArray:
        s = s + a * 2 ** i   
        i+= 1
    return s

def sumCi(Cis):
    CSum = MiniNero.identity()
    for i in Cis:
        CSum = MiniNero.addKeys(CSum, i)
    return CSum

def sumCiExp(Cis, Exp):
    #Cis is a vector
    #Exp is a vector
    CSum = MiniNero.identity()
    for i in range(0, len(Cis)):
        CSum = MiniNero.addKeys(CSum, MiniNero.scalarmultKey(Cis[i], MiniNero.intToHex(10 ** Exp[i])))
    return CSum


def genRangeProof(b, digits):
    bb = binary(b, digits) #gives binary form of bb in "digits" binary digits
    print("b, b in binary", b, bb)
    ai = [None] * len(bb)
    Ci = [None] * len(bb)
    CiH = [None] * len(bb) #this is like Ci - 2^i H
    a = MiniNero.intToHex(0)
    ii = [None] * len(bb)
    indi = [None] * len(bb)
    for i in range(0, len(bb)):
        ai[i] = PaperWallet.skGen()
        a = MiniNero.addScalars(a, ai[i]) #creating the total mask since you have to pass this to receiver...
        Ci[i] = MiniNero.addKeys(MiniNero.scalarmultBase(ai[i]), MiniNero.scalarmultKey(getHForCT(), MiniNero.intToHex(bb[i] * 2 ** i)))
        CiH[i] = MiniNero.subKeys(Ci[i], MiniNero.scalarmultKey(getHForCT(), MiniNero.intToHex(2 ** i)))
    L1, s2, s = AggregateSchnorr.GenASNL(ai, Ci, CiH, bb)
    return sumCi(Ci), Ci, L1, s2, s, a

def verRangeProof(Ci, L1, s2, s):
    n = len(Ci) #note there will be some fixed length eventually so you can't just get the top digit
    CiH = [None] * n
    for i in range(0, n):
        CiH[i] = MiniNero.subKeys(Ci[i], MiniNero.scalarmultKey(getHForCT(), MiniNero.intToHex(2 ** i)))
    return AggregateSchnorr.VerASNL(Ci, CiH, L1, s2, s) 

def ComputeReceivedAmount(senderEphemPk, receiverSK, maskedMask, maskedAmount, Ci, exponent):
    ss1, ss2 = ecdh.ecdhretrieve(receiverSK, senderEphemPk)
    mask = MiniNero.sc_sub_keys(maskedMask, ss1)
    CSum = sumCi(Ci)
    bH = MiniNero.subKeys(CSum, MiniNero.scalarmultBase(mask)) #bH = C - aG
    b = MiniNero.sc_sub_keys(maskedAmount, ss2)
    print("received amount:", 10 ** exponent * MiniNero.hexToInt(b))
    H = getHForCT()
    bHTent = MiniNero.scalarmultKey(H, b)
    print(bHTent,"=?", bH)
    if bHTent != bH:
        print("wrong amount sent!")
        return -1
    return 0

def genRCTSig(sk_x, sk_in, sk_out, Pk, CIn, COut, ExpIn, ExpOut, index):
    #sk_x is private keys of addresses (vector)
    #sk_in is masks of input commitments (vector)
    #sk_out is masks of output commitments (vector)
    #Pk is public key list (2d array)
    #CIn is input commitments (2d array)
    #COut is output commitments (vector)
    #ExpIn is exponents for the input commitments (2d array)
    #so each row of this is going to correspond to a column in the actual mlsag..
    #ExpOut is exponents for the output commitments
    #index is the secret index
    sk = sk_x[:]
    sk.append(MiniNero.sc_sub_keys(MiniNero.sc_add(sk_in, ExpIn[index]), MiniNero.sc_add(sk_out, ExpOut)))
    CRow = [None] * len(CIn) #commitments row of public keys Cin - Cout
    COutSum = sumCiExp(COut, ExpOut) #Cout1*10^i_1 + Cout2 * 10^{i_2}..
    tmp = MiniNero.identity()
    pk = [None] * (len(sk_x) + 1) #generalize later...
    pk[0] = Pk
    for i in range(0, len(CIn)):
        CRow[i] = MiniNero.subKeys(sumCiExp(CIn[i], ExpIn[i]), COutSum) 
    pk[1] = CRow
    II, cc, ssVal = MLSAG.MLSAG_Sign(pk, sk, index)
    return pk, II, cc, ssVal

