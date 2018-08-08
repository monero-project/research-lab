# ECIES: a dumb implementation of ECIES encryption
#
# Use this code only for prototyping
# -- putting this code into production would be dumb
# -- assuming this code is secure would also be dumb

import dumb25519
import hashlib
import binascii
from Crypto.Cipher import AES
from Crypto import Random

# define curve points
G = dumb25519.G

class Ciphertext:
    R = None
    e = None
    sigma = None

    def __init__(self,R,e,sigma):
        self.R = R
        self.e = e
        self.sigma = sigma

def gen_private_key():
    return dumb25519.random_scalar()

def gen_public_key(private_key):
    return G*private_key

def encrypt(public_key,tag,message):
    if not isinstance(public_key,dumb25519.Point):
        raise TypeError

    r = dumb25519.random_scalar()
    R = G*r
    P = public_key*r

    hashes = hashlib.sha256(str(P)+str(tag)).hexdigest()
    sym_key = hashes[:len(hashes)/2]
    mac_key = hashes[len(hashes)/2:]

    e = binascii.hexlify(AES.new(sym_key,AES.MODE_CFB,'0'*16).encrypt(str(message)))
    sigma = hashlib.sha256(mac_key+hashlib.sha256(mac_key+e).hexdigest()).hexdigest()

    return Ciphertext(R,e,sigma)

def decrypt(secret_key,tag,ciphertext):
    if not isinstance(secret_key,dumb25519.Scalar):
        raise TypeError
    if not isinstance(ciphertext,Ciphertext):
        raise TypeError

    P = ciphertext.R*secret_key
    
    hashes = hashlib.sha256(str(P)+str(tag)).hexdigest()
    sym_key = hashes[:len(hashes)/2]
    mac_key = hashes[len(hashes)/2:]

    if hashlib.sha256(mac_key+hashlib.sha256(mac_key+ciphertext.e).hexdigest()).hexdigest() != ciphertext.sigma:
        raise Exception('Failed ECIES authentication!')

    return AES.new(sym_key,AES.MODE_CFB,'0'*16).decrypt(binascii.unhexlify(ciphertext.e))
