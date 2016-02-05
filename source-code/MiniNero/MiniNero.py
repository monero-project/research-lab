#"MiniNero" by Shen Noether mrl. Use at your own risk.
import hashlib #for signatures
import math
import Crypto.Random.random as rand
import Keccak #cn_fast_hash
import mnemonic #making 25 word mnemonic to remember your keys
import binascii #conversion between hex, int, and binary. Also for the crc32 thing
import ed25519 #Bernsteins python ed25519 code from cr.yp.to
import zlib

b = 256
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493

def netVersion():
    return "12"

def public_key(sk):
    #returns point encoded to binary .. sk is just an int..
    return ed25519.encodepoint(ed25519.scalarmultbase(sk)) #pub key is not just x coord..

def scalarmult_simple(pk, num):
    #returns point encoded to hex.. num is an int, not a hex
    return ed25519.encodepoint(ed25519.scalarmult(toPoint(pk), num)) #pub key is not just x coord..

def addKeys(P1, P2):
    return binascii.hexlify(ed25519.encodepoint(ed25519.edwards(toPoint(P1), toPoint(P2))))

#aG + bB, G is basepoint..
def addKeys1(a, b, B):
    return addKeys(scalarmultBase(a), scalarmultKey(B, b))

#aA + bB
def addKeys2(a, A, b, B):
    return addKeys(scalarmultKey(A, a), scalarmultKey(B, b))

def subKeys(P1, P2):
    return binascii.hexlify(ed25519.encodepoint(ed25519.edwards_Minus(toPoint(P1), toPoint(P2))))

def randomScalar():
    tmp = rand.getrandbits(32 * 8) # 8 bits to a byte ...  
    return (tmp)

def xor(a, b):
    return intToHex(hexToInt(a) ^ hexToInt(b))

def electrumChecksum(wordlist):
    wl = wordlist.split(" ") #make an array
    if len(wl) > 13:
        wl = wl[:24]
    else:
        wl = wl[:12]
    upl = 3 #prefix length
    wl2 = ''
    for a in wl:
        wl2+= a[:upl]
    z = ((zlib.crc32(wl2) & 0xffffffff) ^ 0xffffffff ) >> 0
    z2 = ((z ^ 0xffffffff) >> 0) % len(wl)
    return wl[z2]

__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

def b58encode(v):
    a = [reverseBytes(v[i:i+16]) for i in range(0, len(v)-16, 16)]
    rr = -2*((len(v) /2 )% 16)

    res = ''
    for b in a:
        bb = hexToInt(b)
        result = ''
        while bb >= __b58base:
            div, mod = divmod(bb, __b58base)
            result = __b58chars[mod] + result
            bb = div
        result = __b58chars[bb] + result
        res += result
    result = ''
    if rr < 0:
        bf =  hexToInt(reverseBytes(v[rr:])) #since we only reversed the ones in the array..
        result = ''
        while bf >= __b58base:
            div, mod = divmod(bf, __b58base)
            result = __b58chars[mod] + result
            bf = div
        result = __b58chars[bf] + result
    res += result
    return res
    
    
def sc_0():
    return intToHex(0)
    
def sc_reduce_key(a):
    return intToHex(hexToInt(a) % l)

def sc_unreduce_key(a):
    return intToHex(hexToInt(a) % l + l)

def sc_add_keys(a, b):
    #adds two private keys mod l
    return intToHex((hexToInt(a) + hexToInt(b)) % l)

def sc_add(a, exps):
    #adds a vector of private keys mod l and multiplies them by an exponent
    ssum = 0
    for i in range(0, len(a)):
        ssum = (ssum + 10 ** exps[i] * hexToInt(a[i])) % l
    return intToHex(ssum)

def sc_check(a):
    if hexToInt(a) % l == 0:
        return False
    return (a == sc_reduce_key(a))

def addScalars(a, b): #to do: remove above and rename to this (so that there is "add keys" and "add scalars")
    #adds two private keys mod l
    return intToHex((hexToInt(a) + hexToInt(b)) % l)

def sc_sub_keys(a, b):
    #subtracts two private keys mod l
    return intToHex((hexToInt(a) - hexToInt(b)) % l)

def sc_mul_keys(a, b):
    return intToHex((hexToInt(a) * hexToInt(b)) % l)

def sc_sub_keys(a, b):
    return intToHex((hexToInt(a) - hexToInt(b)) % l)

def sc_mulsub_keys(a, b, c):
    #returns a - b * c (for use in LLW sigs - see MRL notes v 0.3)
    return intToHex( (hexToInt(a)- hexToInt(b) * hexToInt(c)) % l)

def add_l(a, n):
    return intToHex(hexToInt(a) +n * l )

def sc_muladd_keys(a, b, c):
    #returns a + b * c (for use in LLW sigs - see MRL notes v 0.3)
    return intToHex((hexToInt(a)+ hexToInt(b) * hexToInt(c) ) % l)

def mul_8(a):
    return intToHex(8 * hexToInt(a))

def fe_reduce_key(a):
    return intToHex(hexToInt(a) % q)

def recoverSK(seed):
    mn2 = seed.split(" ") #make array
    if len(mn2) > 13:
        mn2 = mn2[:24]
        sk = mnemonic.mn_decode(mn2)
    else:
        mn2 = mn2[:12]
        #mn2 += mn2[:]
        sk = cn_fast_hash(mnemonic.mn_decode(mn2))
        #sk = mnemonic.mn_decode(mn2)

    return sk

def cn_fast_hash(s):
    k = Keccak.Keccak()
    return k.Keccak((len(s) * 4, s), 1088, 512, 32 * 8, False).lower() #r = bitrate = 1088, c = capacity, n = output length in bits

def getView(sk):
    a = hexToInt(cn_fast_hash(sc_reduce_key(sk))) % l
    return intToHex(a)

def getViewMM(sk):
    a = hexToInt(cn_fast_hash(sk))
    return intToHex(a)


def reverseBytes(a): #input is byte string, it reverse the endianness
    b = [a[i:i+2] for i in range(0, len(a)-1, 2)]
    return ''.join(b[::-1])

def encode_addr(version, spendP, viewP):
    buf = version + spendP + viewP
    h = cn_fast_hash(buf)
    buf = buf +  h[0:8]
    return b58encode(buf)

def hexToInt(h):
    s = binascii.unhexlify(h) #does hex to bytes
    bb = len(h) * 4 #I guess 8 bits / b
    return sum(2**i * ed25519.bit(s,i) for i in range(0,bb)) #does to int

def intToHex(i):
    return binascii.hexlify(ed25519.encodeint(i)) #hexlify does bytes to hex

def publicFromSecret(sk):
    #returns pubkey in hex, same as scalarmultBase
    return binascii.hexlify(public_key(hexToInt(sk)))

def scalarmultBase(sk):
    #returns pubkey in hex, expects hex sk
    return binascii.hexlify(public_key(hexToInt(sk)))

def identity():
    return scalarmultBase(intToHex(0))

def scalarmultKey(pk, num):
   return binascii.hexlify(scalarmult_simple(pk, hexToInt(num)))

def scalarmultKeyInt(pk, num):
   return binascii.hexlify(scalarmult_simple(pk, num))

def publicFromInt(i):
    #returns pubkey in hex, same as scalarmultBase.. should just pick one
    return binascii.hexlify(public_key(i))

def toPoint(hexVal):
    aa = binascii.unhexlify(hexVal) #to binary (new)
    return ed25519.decodepoint(aa) #make to point

def fromPoint(aa): #supposed to reverse toPoint
    binvalue = ed25519.encodepoint(aa)
    return binascii.hexlify(binvalue)

def hashToPoint_cn(hexVal):
    #note this is the monero one, won't work for C.T. 
    #however there is an alternative which will work for C.T.
    #pk = publicFromSecret(hexVal)
    HP = cn_fast_hash(hexVal)
    return scalarmultBase(HP)

def mul8(point):
    return binascii.hexlify(scalarmult_simple(point, 8))

def hashToPoint_ct(hexVal):
    #note this is the monero one, won't work for C.T. 
    #however there is an alternative which will work for C.T.
    #returns a hex string, not a point
    a = hexVal[:]
    i = 0
    while True:
        worked = 1
        a = cn_fast_hash(a)
        i += 1
        try:
            toPoint(a)
        except:
            worked = 0
        if worked == 1:
            break
    print("found point after "+str(i)+" hashes")
    return mul8(a) # needs to be in group of basepoint
    
def getAddrMM(sk):
    vk = getViewMM(sk)
    sk = sc_reduce_key(sk)
    pk = publicFromSecret(sk)
    pvk = publicFromSecret(vk)
    return encode_addr(netVersion(), pk, pvk)

def getAddr(sk):
    vk = getView(sk)
    sk = sc_reduce_key(sk)
    pk = publicFromSecret(sk)
    pvk = publicFromSecret(vk)
    return encode_addr(netVersion(), pk, pvk)
