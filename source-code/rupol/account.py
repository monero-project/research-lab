# RuPol: a dumb implementation of Ruffing's polynomial ring confidential scheme
#
# Use this code only for prototyping
# -- putting this code into production would be dumb
# -- assuming this code is secure would also be dumb

import dumb25519
import ecies
import stealth

# define curve points
G = dumb25519.G
H = dumb25519.H
T = dumb25519.T

class Account:
    pk = None
    co = None
    _ek = None
    _a = None
    _r = None

    def __init__(self,pk,co,_ek,_a,_r):
        self.pk = pk
        self.co = co
        self._ek = _ek
        self._a = _a
        self._r = _r

def gen_account(public_key,a):
    r = dumb25519.random_scalar()
    co = G*a + H*r

    ek = dumb25519.random_scalar()
    s = dumb25519.hash_to_scalar(str(public_key.tpk)+str(public_key.spk)+str(ek))
    pk = public_key.X + H*s

    _ek = ecies.encrypt(public_key.tpk,str(pk)+str(co),str(ek))
    _a = ecies.encrypt(public_key.spk,str(pk)+str(co),str(a))
    _r = ecies.encrypt(public_key.spk,str(pk)+str(co),str(r))

    return Account(pk,co,_ek,_a,_r)

def recover_withdrawal(private_key,account):
    ek = dumb25519.Scalar(int(ecies.decrypt(private_key.tsk,str(account.pk)+str(account.co),account._ek)))
    a = dumb25519.Scalar(int(ecies.decrypt(private_key.ssk,str(account.pk)+str(account.co),account._a)))
    r = dumb25519.Scalar(int(ecies.decrypt(private_key.ssk,str(account.pk)+str(account.co),account._r)))

    public_key = stealth.gen_public_key(private_key)
    s = dumb25519.hash_to_scalar(str(public_key.tpk)+str(public_key.spk)+str(ek))

    if G*a + H*r != account.co:
        raise Exception('Bad account commitment!')
    if public_key.X + H*s != account.pk:
        raise Exception('Bad account public key!')

    xs = private_key.x+s
    return private_key.x+s,a,r,T*xs.invert()
