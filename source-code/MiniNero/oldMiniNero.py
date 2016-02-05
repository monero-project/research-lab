########################################################################
#     MiniNero.py
#A miniature, commented
#port of CryptoNote and 
#Monero: 
#     crypto.cpp / crypto-ops.cpp
#
#Using Bernstein's ed25519.py for the curve stuff.
#The main point is to have a model what's happening in CryptoNote
#             -Shen.Noether
#
#Note: The ring image function seems
# to take a lot of memory to run
# it will throw strange errors if
# your computer doesn't have 
# enough
#Note2: 
# As of yet, slightly incompatible, although mathematically equivalent.
# The discrepancies are some differences in packing and hashing.
#
# To the extent possible under law, the implementer has waived all copyright
# and related or neighboring rights to the source code in this file.
# http://creativecommons.org/publicdomain/zero/1.0/
#
#The parts of code from Bernstein(?)'s library possibly has it's own license
# which you can dig up from http://cr.yp.to/djb.html
########################################################################



import hashlib
import struct
import base64
import binascii
import sys
from Crypto.Util import number
import Crypto.Random.random as rand
import Keccak
from collections import namedtuple
import copy

KEK=Keccak.Keccak(1600)
CURVE_P = (2**255 - 19)
b = 256
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493
BASEPOINT = "0900000000000000000000000000000000000000000000000000000000000000"

#####################################
#Bernstein(?) Eddie Library in python
#####################################

def H(m):
    return hashlib.sha512(m).digest()

def expmod(b,e,m):
    if e == 0: return 1
    t = expmod(b,e/2,m)**2 % m
    if e & 1: t = (t*b) % m
    return t

def inv(x):
    return expmod(x,q-2,q)

d = -121665 * inv(121666)
I = expmod(2,(q-1)/4,q)

def xrecover(y):
    xx = (y*y-1) * inv(d*y*y+1)
    x = expmod(xx,(q+3)/8,q)
    if (x*x - xx) % q != 0: x = (x*I) % q
    if x % 2 != 0: x = q-x
    return x

By = 4 * inv(5)
Bx = xrecover(By)
B = [Bx % q,By % q]

def edwards(P,Q):
    x1 = P[0]
    y1 = P[1]
    x2 = Q[0]
    y2 = Q[1]
    x3 = (x1*y2+x2*y1) * inv(1+d*x1*x2*y1*y2)
    y3 = (y1*y2+x1*x2) * inv(1-d*x1*x2*y1*y2)
    return [x3 % q,y3 % q]

def scalarmult(P, e):
    if e == 0: return [0,1]
    Q = scalarmult(P,e/2)
    Q = edwards(Q,Q)
    if e & 1: Q = edwards(Q,P)
    return Q

def encodeint(y):
    bits = [(y >> i) & 1 for i in range(b)]
    return ''.join([chr(sum([bits[i * 8 + j] << j for j in range(8)])) for i in range(b/8)])

def encodepoint(P):
    x = P[0]
    y = P[1]
    bits = [(y >> i) & 1 for i in range(b - 1)] + [x & 1]
    return ''.join([chr(sum([bits[i * 8 + j] << j for j in range(8)])) for i in range(b/8)])

def bit(h,i):
    return (ord(h[i/8]) >> (i%8)) & 1

def public_key(sk):
    A = scalarmult(B,sk)
    return encodepoint(A)


def Hint(m):
    h = H(m)
    return sum(2**i * bit(h,i) for i in range(2*b))

def signature(m,sk,pk):
    h = H(sk)
    a = 2**(b-2) + sum(2**i * bit(h,i) for i in range(3,b-2))
    r = Hint(''.join([h[i] for i in range(b/8,b/4)]) + m)
    R = scalarmult(B,r)
    S = (r + Hint(encodepoint(R) + pk + m) * a) % l
    return encodepoint(R) + encodeint(S)

def isoncurve(P):
    x = P[0]
    y = P[1]
    return (-x*x + y*y - 1 - d*x*x*y*y) % q == 0

def decodeint(s):
    return sum(2**i * bit(s,i) for i in range(0,b))

def decodepoint(s):
    y = sum(2**i * bit(s,i) for i in range(0,b-1))
    x = xrecover(y)
    if x & 1 != bit(s,b-1): x = q-x
    P = [x,y]
    if not isoncurve(P): raise Exception("decoding point that is not on curve")
    return P

def checkvalid(s,m,pk):
    if len(s) != b/4: raise Exception("signature length is wrong")
    if len(pk) != b/8: raise Exception("public-key length is wrong")
    R = decodepoint(s[0:b/8])
    A = decodepoint(pk)
    S = decodeint(s[b/8:b/4])
    h = Hint(encodepoint(R) + pk + m)
    if scalarmult(B,S) != edwards(R,scalarmult(A,h)):
        raise Exception("signature does not pass verification")

#################################
#curve stuff, 
#mostly from https://github.com/monero-project/bitmonero/blob/1b8a68f6c1abcf481652c2cfd87300a128e3eb32/src/crypto/crypto-ops.c
#partial reference for fe things https://godoc.org/github.com/agl/ed25519/edwards25519
#note ge is the edwards version of the curve
#fe is the monty version of the curve
#################################


#NOT USED IN MININERO - Use ge_scalarmult_base
def ge_fromfe_frombytesvartime(s):
    #inputs something s (I assume in bytes)
    #inputs into montgomery form (fe)
    #then, turns it into edwards form (ge)
    #then r is the edwards curve point r->
    #reference 1: http://crypto.stackexchange.com/questions/9536/converting-ed25519-public-key-to-a-curve25519-public-key?rq=1
    #reference 2: https://github.com/orlp/ed25519/blob/master/src/key_exchange.c
    #best reference https://www.imperialviolet.org/2013/12/25/elligator.html
    
    #the point of this function is to return a ge_p2 from an int s
    #whereas, the similar function ge_frombytes_vartime returns a gep3
    return

def ge_double_scalarmult_base_vartime(aa, AA, bb):
    #a very nice comment in the CN code for this one!
    #r = a * A + b * B
    #where a = a[0]+256*a[1]+...+256^31 a[31].
    #and b = b[0]+256*b[1]+...+256^31 b[31].
    #B is the Ed25519 base point (x,4/5) with x positive.
    #cf also https://godoc.org/github.com/agl/ed25519/edwards25519
    tmpa = ge_scalarmult(aa, AA)
    tmpb = ge_scalarmult(bb, BASEPOINT)
    return toHex(edwards(toPoint(tmpa), toPoint(tmpb)))

def ge_double_scalarmult_vartime(aa, AA, bb, BB):
    #a very nice comment in the CN code for this one!
    #r = a * A + b * B
    #where a = a[0]+256*a[1]+...+256^31 a[31].
    #and b = b[0]+256*b[1]+...+256^31 b[31].
    #B is the Ed25519 base point (x,4/5) with x positive.
    #cf also https://godoc.org/github.com/agl/ed25519/edwards25519
    tmpa = ge_scalarmult(aa, AA)
    tmpb = ge_scalarmult(bb, BB)
    return toHex(edwards(toPoint(tmpa), toPoint(tmpb)))


def toPoint(pubkey):
    #turns hex key into x, y field coords
    return decodepoint(pubkey.decode("hex"))

def toHex(point):
    #turns point into pubkey (reverse of toPoint)
    return encodepoint(point).encode("hex")

def ge_scalarmult(a, A):
    #so I guess given any point A, and an integer a, this computes aA
    #so the seecond arguement is definitely an EC point
    # from http://cr.yp.to/highspeed/naclcrypto-20090310.pdf
    # "Alice's secret key a is a uniform random 32-byte string then 
    #clampC(a) is a uniform random Curve25519 secret key
    #i.e. n, where n/8 is a uniform random integer between 
    #2^251 and 2^252-1
    #Alice's public key is n/Q compressed to the x-coordinate
    #so that means, ge_scalarmult is not actually doing scalar mult
    #clamping makes the secret be between 2^251 and 2^252
    #and should really be done
    #print(toPoint(A))
    return encodepoint(scalarmult(toPoint(A), a)).encode("hex") # now using the eddie function

def ge_scalarmult_base(a):
    #in this function in the original code, they've assumed it's already clamped ... 
    #c.f. also https://godoc.org/github.com/agl/ed25519/edwards25519
    #it will return h = a*B, where B is ed25519 bp (x,4/5)
    #and a = a[0] + 256a[1] + ... + 256^31 a[31]
    #it assumes that a[31 <= 127 already
    return ge_scalarmult(8*a, BASEPOINT)

#NOT USED IN MININERO - use ge_scalarmult_base
def ge_frombytes_vartime(key):
    #https://www.imperialviolet.org/2013/12/25/elligator.html
    #basically it takes some bytes of data
    #converts to a point on the edwards curve
    #if the bytes aren't on the curve
    #also does some checking on the numbers
    #ex. your secret key has to be at least >=4294967277
    #also it rejects certain curve points, i.e. "if x = 0, sign must be positive
    return 0

#NOT USED IN MININERO - unecessary as all operations are from hex
def ge_p1p1_to_p2(p):
    #there are two ways of representing the points
    ##http://code.metager.de/source/xref/lib/nacl/20110221/crypto_sign/edwards25519sha512batch/ref/ge25519.c
    #http://www.hyperelliptic.org/EFD/g1p/auto-twisted-extended-1.html
    return

#NOT USED IN MININERO -unnecessary as operations are from hex
def ge_p2_dbl():
    #basically it doubles a point and doubles it
    #c.f. Explicit Formulas for Doubling (towards bottom)
    #Explicit formulas for doubling
    #http://www.hyperelliptic.org/EFD/g1p/auto-twisted-extended-1.html
    return

#NOT USED IN MININERO - unnecessary as operations are from hex
def ge_p3_to_p2():
    #basically, it copies a point in 3 coordinates to another point
    #c.f. Explicit Formulas for Doubling (towards bottom)
    #Explicit formulas for doubling
    #http://www.hyperelliptic.org/EFD/g1p/auto-twisted-extended-1.html
    return

def ge_mul8(P):
    #ok, the point of this is to double three times
    #and the point is that the ge_p2_dbl returns a point in the p1p1 form
    #so that's why have to convert it first and then double
    return ge_scalarmult(8, P)

def sc_reduce(s):
    #inputs a 64 byte int and outputs the lowest 32 bytes
    #used by hash_to_scalar, which turns cn_fast_hash to number..
    r = longToHex(s)
    r = r[64::] 
    #print("before mod p", r)
    return hexToLong(r) % CURVE_P

def sc_reduce32(data):
    #ok, the code here is exactly the same as sc_reduce
    #(which is default lib sodium)
    #except it is assumed that your input
    #s is alread in the form:
    # s[0]+256*s[1]+...+256^31*s[31] = s
    #and the rest is just reducing mod l
    #so basically take a 32 byte input, and reduce modulo the prime
    return data % CURVE_P 

def sc_mulsub(a, b, c):
    #takes in a, b, and c
    #This is used by the regular sig 
    #i.e. in generate_signature
    #returns c-ab mod l
    a = number.bytes_to_long(a[::-1])
    b = number.bytes_to_long(b[::-1])
    c = number.bytes_to_long(c[::-1])
    return (c - a * b) % CURVE_P


##########################################
#Hashing
#this is where keccak, H_p, and H_s come in..
######################################

def cn_fast_hash(key, size):
    #see ReadMeKeccak.txt
    return KEK.Keccak((size,key.encode("hex")),1088,512,256,False)


###################################################
#CryptoNote Things
#Mainly from https://github.com/monero-project/bitmonero/blob/1b8a68f6c1abcf481652c2cfd87300a128e3eb32/src/crypto/crypto.cpp
###################################################

def random_scalar():
    tmp = rand.getrandbits(64 * 8) # 8 bits to a byte ...  
    tmp = sc_reduce(tmp) #-> turns 64 to 32 (note sure why don't just gt 32 in first place ... )
    return tmp

def hash_to_scalar(data, length):
    #this one is H_s(P)
    #relies on cn_fast_hash and sc_reduce32 (which makes an int smaller)
    #the input here is not necessarily a 64 byte thing, and that's why sc_reduce32 
    res = hexToLong(cn_fast_hash(data, length))
    return sc_reduce32(res)
    

def generate_keys():
    #should return a secret key and public key pair
    #once you have the secret key,
    #then the public key be gotten from 25519 function
    #so just need to generate random
    #first generate random 32-byte(256 bit) integer, copy to result
    #ok, just sc_reduce, what that does is takes 64 byte int, turns into 32 byte int...
    #so sc_reduce is legit and comes from another library http://hackage.haskell.org/package/ed25519-0.0.2.0/src/src/cbits/sc_reduce.c
    #as far as I can tell, sc
    #basically this gets you an int which is sufficiently large
    #import Crypto.Random.random as rand
    rng = random_scalar()
    #sec = hex(rng).rstrip("L").lstrip("0x") or "0"
    sec = sc_reduce32(rng)
    pub = public_key(sec).encode("hex")
    #pub = ge_scalarmult_base(sec)
    #print(rng.decode("hex"))
    #sec = curve25519_mult(rng, basepoint)

    #the point of ge_p3_tobytes here is just store as bytes...
    #and p3 is a way to store points on the ge curve
    return sec, pub

def check_key(key):
    #inputs a public key, and outputs if point is on the curve
    return isoncurve(toPoint(key))

def secret_key_to_public_key(secret_key):
    #the actual function returns as bytes since they mult the fast way.
    if sc_check(secret_key) != 0:
        print "error in sc_check"
        quit()
    return public_key(secret_key)

def hash_to_ec(key):
    #takes a hash and turns into a point on the curve
    #In MININERO, I'm not using the byte representation
    #So this function is superfluous
    h = hash_to_scalar(key, len(key))
    point = ge_scalarmult_base(h)
    return ge_mul8(point)


def generate_key_image(public_key, secret_key):
    #should return a key image as defined in whitepaper
    if sc_check(secret_key) != 0:
        print"sc check error in key image"
    point = hash_to_ec(public_key)
    point2 = ge_scalarmult(secret_key, point)
    return point2 

def generate_ring_signature(prefix, image, pubs, pubs_count, sec, sec_index):
    #returns a ring signature
    if sec_index >= pubs_count:
        print "bad index of secret key!"
        quit()
    if ge_frombytes_vartime(image) != 0:
        print"bad image!"
        quit()
    summ = 0
    aba = [0 for xx in range(pubs_count)] 
    abb = [0 for xx in range(pubs_count)] 
    sigc = [0 for xx in range(pubs_count)] #these are the c[i]'s from the whitepaper
    sigr =[0 for xx in range(pubs_count)] #these are the r[i]'s from the whitepaper
    for ii in range(0, pubs_count):
        if (ii == sec_index):
            kk = random_scalar()
            tmp3 = ge_scalarmult_base(kk) #L[i] for i = s
            aba[ii] = tmp3
            tmp3 = hash_to_ec(pubs[ii]) #R[i] for i = s
            abb[ii] = ge_scalarmult(kk, tmp3) 
        else:
            k1 = random_scalar() #note this generates a random scalar in the correct range...
            k2 = random_scalar()
            if ge_frombytes_vartime(pubs[ii]) != 0:
                print "error in ring sig!!!"
                quit()
            tmp2 = ge_double_scalarmult_base_vartime(k1, pubs[ii], k2) #this is L[i] for i != s
            aba[ii] = tmp2
            tmp3 = hash_to_ec(pubs[ii])
            abb[ii] = ge_double_scalarmult_vartime(k2, tmp3, k1, image) #R[i] for i != s
            sigc[ii] = k1  #the random c[i] for i != s
            sigr[ii] = k2  #the random r[i] for i != s
            summ = sc_add(summ, sigc[ii]) #summing the c[i] to get the c[s] via page 9 whitepaper
    
    buf = struct.pack('64s', prefix)
    for ii in range(0, pubs_count):
        buf += struct.pack('64s', aba[ii])
        buf += struct.pack('64s', abb[ii])
    hh = hash_to_scalar(buf,len(buf))
    sigc[sec_index] = sc_sub(hh, summ) # c[s] = hash - sum c[i] mod l
    sigr[sec_index] = sc_mulsub(sigc[sec_index], sec, kk) # r[s] = q[s] - sec * c[index]
    return image, sigc, sigr


            
     


def check_ring_signature(prefix, key_image, pubs, pubs_count, sigr, sigc):
    #from https://github.com/monero-project/bitmonero/blob/6a70de32bf872d97f9eebc7564f1ee41ff149c36/src/crypto/crypto.cpp
    #this is the "ver" algorithm
    aba = [0 for xx in range(pubs_count)] 
    abb = [0 for xx in range(pubs_count)] 

    if ge_frombytes_vartime(key_image) != 0:
        print "ring image error in checking sigs"
        quit()
    summ = 0
    buf = struct.pack('64s', prefix)
    for ii in range(0, pubs_count):
        if ((sc_check(sigc[ii]) != 0) or (sc_check(sigr[ii]) != 0)):
            print "failed sc_check in check ring sigs"
            quit()
        if ge_frombytes_vartime(pubs[ii]) != 0:
            print "public key is a bad point in ring sigs"
            quit()

        tmp2 = ge_double_scalarmult_base_vartime(sigc[ii], pubs[ii], sigr[ii]) 
        aba[ii] = tmp2
        tmp3 = hash_to_ec(pubs[ii])
        tmp2 = ge_double_scalarmult_vartime(sigr[ii], tmp3, sigc[ii], key_image)
        abb[ii] = tmp2
        summ = sc_add(summ, sigc[ii])
    for ii in range(0, pubs_count):
        buf += struct.pack('64s', aba[ii])
        buf += struct.pack('64s', abb[ii])
    
    hh = hash_to_scalar(buf,len(buf))
    hh = sc_sub(hh, summ)
    return sc_isnonzero(hh) == 0

def generate_key_derivation(key1, key2):
    #key1 is public key of receiver Bob (see page 7)
    #key2 is Alice's private
    #this is a helper function for the key-derivation
    #which is the generating one-time key's thingy
    if sc_check(key2) != 0:
        #checks that the secret key is uniform enough... 
        print"error in sc_check in keyder"
        quit()
    if ge_frombytes_vartime(key1) != 0:
        print "didn't pass curve checks in keyder"
        quit()
    
    point = key1 ## this ones the public
    point2 = ge_scalarmult( key2, point)
    #print("p2", encodepoint(point2).encode("hex"))
    point3 = ge_mul8(point2) #This has to do with n==0 mod 8 by dedfinition, c.f. the top paragraph of page 5 of http://cr.yp.to/ecdh/curve25519-20060209.pdf
    #and also c.f. middle of page 8 in same document (Bernstein)
    return point3

def derivation_to_scalar(derivation, output_index):
    #this function specifically hashes your
    #output index (for the one time keys )
    #in order to get an int, so we can do ge_mult_scalar
    #buf = s_comm(d = derivation, o = output_index)
    buf2 = struct.pack('64sl', derivation, output_index) 
    #print(buf2)
    return hash_to_scalar(buf2, len(buf2))

def derive_public_key(derivation, output_index, base ):
    if ge_frombytes_vartime(base) != 0: #check some conditions on the point
        print"derive pub key bad point"
        quit()
    point1 = base
    scalar = derivation_to_scalar(derivation, output_index)
    point2 = ge_scalarmult_base(scalar)
    point3 = point2 #I think the cached is just for the sake of adding
    #because the CN code adds using the monty curve
    point4 = edwards(toPoint(point1), toPoint(point3))
    return point4

def sc_add(aa, bb):
    return (aa + bb ) %CURVE_P
def sc_sub(aa, bb):
    return (aa - bb ) %CURVE_P

def sc_isnonzero(c):
    return (c %CURVE_P != 0 )

def sc_mulsub(aa, bb, cc):
    return (cc - aa * bb ) %CURVE_P

def derive_secret_key(derivation, output_index, base):
    #outputs a derived key...
    if sc_check(base) !=0:
        print"cs_check in derive_secret_key"
    scalar = derivation_to_scalar(derivation, output_index)
    return base + scalar
    
class s_comm:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

def generate_signature(prefix_hash, pub, sec):
    #gets the "usual" signature (not ring sig)
    #buf = s_comm(h=prefix_hash, key=pub, comm=0) #see the pack below
    k = random_scalar()
    tmp3 = ge_scalarmult_base(k)
    buf2 = struct.pack('64s64s64s', prefix_hash, pub, tmp3) 
    sigc = hash_to_scalar(buf2, len(buf2))
    return sc_mulsub(sigc, sec, k), sigc

def check_signature(prefix_hash, pub, sigr, sigc):
    #checking the normal sigs, not the ring sigs...
    if ge_frombytes_vartime(pub) !=0:
        print "bad point, check sig!"
        quit() 
    if (sc_check(sigc) != 0) or (sc_check(sigr) != 0):
        print"sc checksig error!"
        quit() 
    tmp2 = ge_double_scalarmult_base_vartime(sigc, pub, sigr)
    buf2 = struct.pack('64s64s64s', prefix_hash, pub, tmp2) 
    c = hash_to_scalar(buf2, len(buf2))
    c = sc_sub(c, sigc)
    return sc_isnonzero(c) == 0

def hexToLong(a):
    return number.bytes_to_long(a.decode("hex"))

def longToHex(a):
    return number.long_to_bytes(a).encode("hex")

def hexToBits(a):
    return a.decode("hex")

def bitsToHex(a):
    return a.encode("hex")

def sc_check(key):
    #in other words, keys which are too small are rejected
    return 0 
    #s0, s1, s2, s3, s4, s5, s6, s7 = load_4(longToHex(key))
    #return (signum_(1559614444 - s0) + (signum_(1477600026 - s1) << 1) + (signum_(2734136534 - s2) << 2) + (signum_(350157278 - s3) << 3) + (signum_(-s4) << 4) + (signum_(-s5) << 5) + (signum_(-s6) << 6) + (signum_(268435456 - s7) << 7)) >> 8


if __name__ == "__main__":
    if sys.argv[1] == "rs":
        #test random_scalar
        print(longToHex(random_scalar()))
    if sys.argv[1] == "keys":
        #test generating keys
        x,P = generate_keys()
        print"generating keys:"
        print("secret:")
        print( x)
        print("public:")
        print( P)
        print("the point P")
        print(decodepoint(P.decode("hex")))
    if sys.argv[1] == "fasthash":
        mysecret = "99b66345829d8c05041eea1ba1ed5b2984c3e5ec7a756ef053473c7f22b49f14"
        output_index = 2
        buf2 = struct.pack('64sl', mysecret, output_index) 
        #buf2 = pickle(buf)
        #print(buf2)
        print(buf2)
        print(cn_fast_hash(mysecret, len(mysecret)))
        print(cn_fast_hash(buf2, len(buf2)))
 
    if sys.argv[1] == "hashscalar":
        data = "ILOVECATS"
        print(cn_fast_hash(data, len(data)))
        print(hash_to_scalar(data, len(data)))
    if sys.argv[1] == "hashcurve":
        data = "ILOVECATS"
        print(cn_fast_hash(data, len(data)))
        print(hash_to_ec(data))

    if sys.argv[1] == "checkkey":
        x, P = generate_keys()
        print(check_key(P))        
    if sys.argv[1] == "secpub":
        #testing for secret_key_to_public_key
        #these test vecs were for the monty implementation
        mysecret = "99b66345829d8c05041eea1ba1ed5b2984c3e5ec7a756ef053473c7f22b49f14"
        mypublic = "b1c652786697a5feef36a56f36fde524a21193f4e563627977ab515f600fdb3a"
        mysecret, P = generate_keys() 
        pub2 = secret_key_to_public_key(mysecret)
        print(pub2.encode("hex"))
    if sys.argv[1] == "keyder":
        #testing for generate_key_derivation
        x,P = generate_keys()
        print(x, P)
        print(generate_key_derivation(P, x))

    if sys.argv[1] == "dersca":
        #testing for derivation_to_scalar
        #this is getting a scalar for one-time-keys rH_s(P)
        aa, AA = generate_keys()
        bb, BB = generate_keys()
        for i in range(0,3):
            rr, ZZ = generate_keys()
            derivation = generate_key_derivation(BB, aa)
            s = derivation_to_scalar(derivation, i)
            print(s)
    if sys.argv[1] == "derpub":
        x, P = generate_keys()
        output_index = 5
        keyder = generate_key_derivation(P, x)
        print("keyder", keyder)
        print(derive_public_key(keyder, output_index, P))
    if sys.argv[1] == "dersec":
        x, P = generate_keys()
        output_index = 5
        keyder = generate_key_derivation(P, x)
        print("keyder", keyder)
        print(derive_secret_key(keyder, output_index, x))
    if sys.argv[1] == "testcomm":
        a = "99b66345829d8c05041eea1ba1ed5b2984c3e5ec7a756ef053473c7f22b49f14"
        co2 = struct.pack('hhl', 1, 2, 3)
        print(co2.encode("hex")) #sometimes doesn't print if your terminal doesn't have unicode
        
    if sys.argv[1] == "gensig":
        #testing generate_signature
        print""
        prefix = "destination"
        sec, pub  = generate_keys() # just to have some data to use ..
        print(generate_signature(prefix, pub, sec))
    if sys.argv[1] == "checksig":
        prefix = "destination"
        sec, pub  = generate_keys() # just to have some data to use ..
        sir, sic = generate_signature(prefix, pub, sec)
        print(sir, sic)
        print(check_signature(prefix, pub, sir, sic))
    if sys.argv[1] == "keyimage":
        x, P = generate_keys()
        xb = 14662008266461539177776197088974240017016792645044069572180060425138978088469
        Pb = "1d0ecd1758a685d88b39567f491bc93129f59c7dae7182bddc4e6f5ad38ba462"

        I = generate_key_image(Pb, xb)
        print(I) 
    if sys.argv[1] == "ringsig":
        #these are fixed since my computer runs out of memory
        xa = 54592381732429499113512315392038591381134951436395595620076310715410049314218
        Pa = "3c853b5a82912313b179e40d655003c5e3112c041fcf755c3f09d2a8c64d9062"
        xb = 14662008266461539177776197088974240017016792645044069572180060425138978088469
        Pb = "1d0ecd1758a685d88b39567f491bc93129f59c7dae7182bddc4e6f5ad38ba462"
        ima = "0620b888780351a3029dfbf1a5c45a89816f118aa63fa807d51b959cb3c5efc9"
        ima, sic, sir = generate_ring_signature("dest", ima, [Pa, Pb],2,  xb, 1)

        print("ima",ima)
        print("sic", sir)
        print("sir", sic)
        print(check_ring_signature("dest", ima, [Pa, Pb], 2, sir, sic))

    if sys.argv[1] == "conv":
        #testing reduction
        a = "99b66345829d8c05041eea1ba1ed5b2984c3e5ec7a756ef053473c7f22b49f14"
        print(a)
        r = hexToLong(a)
        print(r)
        a = longToHex(r)
        print(a)
    if sys.argv[1] == "red":
        a = "99b66345829d8c05041eea1ba1ed5b2984c3e5ec7a756ef053473c7f22b49f14"
        tmp = rand.getrandbits(64 * 8)
        tmp2 = longToHex(tmp)
        print(tmp2)
        tmp3 = longToHex(sc_reduce(tmp))
        print(tmp3)
        tmp4 = sc_reduce32(CURVE_P + 1)
        print(tmp4)
        tmp5 = sc_reduce(CURVE_P + 1)
        print(tmp5)
    if sys.argv[1] == "gedb":
        x, P = generate_keys()
        print(ge_double_scalarmult_base_vartime(x, P, x))
    if sys.argv[1] == "sck":
        #testing sc_check
        x, P = generate_keys()
        print(sc_check(x))
        print("nonreduced", longToHex(x))
        print("reduced", sc_reduce32_2(x))
        print("check reduced", sc_check(hexToLong(sc_reduce32_2(x))))
    

        


        
        

