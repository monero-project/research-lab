import MiniNero
import os
import ed25519
import binascii
import PaperWallet

import json, hmac, hashlib, time, requests



def HexSigningPubKey(s):
  return binascii.hexlify(ed25519.publickey(ed25519.encodeint(MiniNero.hexToInt(s))))

def Signature(m, sk):
  sk2 = ed25519.encodeint(MiniNero.hexToInt(sk))
  pk = ed25519.publickey(sk2)
  return binascii.hexlify(ed25519.signature(m, sk2, pk))

def Verify(sig, m, pk):
  return ed25519.checkvalid(binascii.unhexlify(sig), m, binascii.unhexlify(pk))
  
#get saved access pubkey
from MiniNeroPubKey import *
pubkey = MiniNeroPk

#ip = raw_input('ip of your server\n')
ip = '192.168.2.112:8080' #hopefully you save this in your app...
ip = '192.168.137.235:8080'
ip = raw_input('your ip?\n')
ip = ip + ':8080'
#sec = raw_input('you secret key?\n')
timestamp = str(int(time.time()))
r = requests.get("http://"+ip +'/api/mininero/')
print r.text
print("your time - server time is:", int(time.time()) - int(r.text))
