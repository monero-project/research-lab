#!/usr/bin/python

#Some code to do the same thing as btcproof (since I think there may be an error in their file hashing?)
#some of this code is taken from KeyUtils.py on a random github, so if you made that, then thanks
import sys
import ecdsa
import ecdsa.der
import ecdsa.util
import hashlib
import os
import re
import struct

import webbrowser #for qr code of address

b58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
VERSION = 0x00

def base58encode(n):
    result = ''
    while n > 0:
        result = b58[n%58] + result
        n /= 58
    return result

def base256decode(s):
    result = 0
    for c in s:
        result = result * 256 + ord(c)
    return result

def countLeadingChars(s, ch):
    count = 0
    for c in s:
        if c == ch:
            count += 1
        else:
            break
    return count

# https://en.bitcoin.it/wiki/Base58Check_encoding
def base58CheckEncode(version, payload):
    s = chr(version) + payload #concat version
    checksum = hashlib.sha256(hashlib.sha256(s).digest()).digest()[0:4]
    print("checksum", checksum)
    result = s + checksum #concat checksum to end
    leadingZeros = countLeadingChars(result, '\0')
    #return base58encode(base256decode(result))
    return '1' * leadingZeros + base58encode(base256decode(result))

def privateKeyToWif(key_hex):    
    return base58CheckEncode(VERSION, key_hex.decode('hex'))
    
def privateKeyToPublicKey(s):
    sk = ecdsa.SigningKey.from_string(s.decode('hex'), curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    return ('\04' + sk.verifying_key.to_string()).encode('hex')
    
def pubKeyToAddr(s):
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hashlib.sha256(s.decode('hex')).digest())
    return base58CheckEncode(0, ripemd160.digest())

def keyToAddr(s):
    return pubKeyToAddr(privateKeyToPublicKey(s))

## below tto create digest of file, result should not vary with blocksize
BLOCKSIZE = 2 **10

def sha256OfFile(filepath):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            block = f.read(BLOCKSIZE)
            if len(block) < BLOCKSIZE: 
                print(len(block))
                block = block[:-1] 
            if not block: break
            sha.update(block)
        return sha.hexdigest()


##proofs, c.f. 
#https://www.btproof.com/technical.html
# hash = SHA256(DATA) // or the supplied hash 
#vhash = CONCAT(VERSION_BYTE, RIPEMD160(hash)) // VERSION_BYTE is 0x00 for main net
#address = BASE58(CONCAT(vhash, SHA256(SHA256(vhash))[0..3]))

def btcProofOfFile(fi):
    has = sha256OfFile(fi)
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(has)
    address = base58CheckEncode(0, ripemd160.digest())
    return address

def btcProofOfString(strin):
    sha = hashlib.sha256()
    sha.update(strin)
    has = sha.digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(has)
    address = base58CheckEncode(0, ripemd160.digest())
    return address



# Generate a random private key
#private_key = os.urandom(32).encode('hex')
#address = base58CheckEncode(version, payload)

#this works (check sha test vectors at http://www.di-mgt.com.au/sha_testvectors.html) indicating I am hashing the file correctly
#print(sha256OfFile("a.txt"))
#print("should be: cdc76e5c 9914fb92 81a1c7e2 84d73e67 f1809a48 a497200e 046d39cc c7112cd0")


#this works
#print("address for abc")
#print(btcProofOfString("abc"))
#this does not agree with btcproof.com, indicating they are hashing file wrong
#print("address for a.txt")
#print(btcProofOfFile("a.txt"))

#print("bitcoin:"+btcProofOfFile(sys.argv[1])+"?amount=0.0001")
a = btcProofOfFile(sys.argv[1])
print(a)
#bitcoin:1PZmMahjbfsTy6DsaRyfStzoWTPppWwDnZ?amount=0.1
#url = "https://chart.googleapis.com/chart?chs=250x250&cht=qr&chl="+a
url2 = "https://blockchain.info/address/"+a
#print(url)
print(url2)
#webbrowser.open(url)
webbrowser.open(url2)
