# RuPol: a dumb implementation of a draft ring confidential transaction scheme
#
# Use this code only for prototyping
# -- putting this code into production would be dumb
# -- assuming this code is secure would also be dumb

import dumb25519
import ecies

# define curve points
G = dumb25519.G
H = dumb25519.H

class PrivateKey:
    tsk = None
    ssk = None
    x = None

    def __init__(self,tsk,ssk,x):
        self.tsk = tsk
        self.ssk = ssk
        self.x = x

class PublicKey:
    tpk = None
    spk = None
    X = None

    def __init__(self,tpk,spk,X):
        self.tpk = tpk
        self.spk = spk
        self.X = X

def gen_private_key():
    return PrivateKey(ecies.gen_private_key(),ecies.gen_private_key(),dumb25519.random_scalar())

def gen_public_key(private_key):
    return PublicKey(ecies.gen_public_key(private_key.tsk),ecies.gen_public_key(private_key.ssk),H*private_key.x)
