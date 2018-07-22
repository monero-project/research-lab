# RuPol: a dumb implementation of a draft ring confidential transaction scheme
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

# protocol parameters
# TODO: make these not arbitrary
p1 = 8 # for n-ary representations
p2 = 8
R = 4 # ring size
beta = dumb25519.l # max amount

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

    def __str__(self):
        return [str(i) for i in [self.pk,self.co,self._ek,self._a,self._r]]

class WithdrawalKey:
    x = None
    a = None
    r = None
    tag = None

    def __init__(self,x,a,r,tag):
        self.x = x
        self.a = a
        self.r = r
        self.tag = tag

class DepositKey:
    a = None
    r = None

    def __init__(self,a,r):
        self.a = a
        self.r = r

class Witness:
    d_ijk = None
    x_i = None
    a_in = None
    a_ij = None
    r_in = None
    r_out = None

    def __init__(self,d_ijk,x_i,a_in,a_ij,r_in,r_out):
        self.d_ijk = d_ijk
        self.x_i = x_i
        self.a_in = a_in
        self.a_ij = a_ij
        self.r_in = r_in
        self.r_out = r_out

class Transaction:
    tags = None
    accounts_ring = None
    accounts_out = None

    def __init__(self,tags,accounts_ring,accounts_out):
        self.tags = tags
        self.accounts_ring = accounts_ring
        self.accounts_out = accounts_out

    def __str__(self):
        return str(self.tags) + str(self.accounts_ring) + str(self.accounts_out)

def gen_account(public_key,a):
    r = dumb25519.random_scalar()
    co = G*a + H*r

    ek = dumb25519.random_scalar()
    s = dumb25519.hash_to_scalar(str(public_key.tpk)+str(public_key.spk)+str(ek))
    pk = public_key.X + H*s

    _ek = ecies.encrypt(public_key.tpk,str(pk)+str(co),str(ek))
    _a = ecies.encrypt(public_key.spk,str(pk)+str(co),str(a))
    _r = ecies.encrypt(public_key.spk,str(pk)+str(co),str(r))

    return Account(pk,co,_ek,_a,_r),DepositKey(a,r)

def receive(private_key,account):
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
    return WithdrawalKey(xs,a,r,T*xs.invert())

# compute the n-ary representation of an integer (lsb is index 0), and pad to a given size
def nary(i,n,pad=None):
    if i < 0 or n < 1:
        raise ArithmeticError
    if pad is not None and pad < 1:
        raise IndexError

    if i == 0:
        bits = [0]
    if i > 0:
        bits = []
        while i > 0:
            i,r = divmod(i,n)
            bits.append(r)
    
    if pad is None or pad <= len(bits):
        return bits
    while pad > len(bits):
        bits.append(0)
    return bits

def prepare_witness(withdrawal_keys,deposit_keys):
    a_in = [withdrawal_key.a for withdrawal_key in withdrawal_keys]
    a_out = [deposit_key.a for deposit_key in deposit_keys]
    r_in = [withdrawal_key.r for withdrawal_key in withdrawal_keys]
    r_out = [deposit_key.r for deposit_key in deposit_keys]

    if len(a_in) != len(r_in) or len(a_out) != len(r_out):
        raise IndexError

    max_i = len(a_in)
    max_j = len(nary(R,p1))
    max_k = p1

    d_ijk = []
    for i in range(max_i):
        d_ijk.append([])
        i_decomp = nary(i,p1,max_j)

        for j in range(max_j):
            d_ijk[i].append([])

            for k in range(max_k):
                if i_decomp[j] == k:
                    d_ijk[i][j].append(dumb25519.Scalar(1))
                else:
                    d_ijk[i][j].append(dumb25519.Scalar(0))

    max_i = len(a_out)
    max_j = len(nary(beta,p2))

    a_ij = []
    for i in range(max_i):
        a_ij.append([dumb25519.Scalar(a) for a in nary(a_out[i].to_int(),p2,max_j)])

    return Witness(d_ijk,[withdrawal_key.x for withdrawal_key in withdrawal_keys],a_in,a_ij,r_in,r_out)

def spend(withdrawal_keys,deposit_keys,tx,mu):
    witness = prepare_witness(withdrawal_keys,deposit_keys)
    witness_list = [witness.d_ijk,witness.x_i,witness.a_in,witness.a_ij,witness.r_in,witness.r_out] # this is so we can flatten for commitment

    t = dumb25519.random_scalar()
    C = dumb25519.pedersen_commit(dumb25519.flatten(witness_list),t)

    s = dumb25519.hash_to_scalar(str(C)+str(tx)+str(mu))
