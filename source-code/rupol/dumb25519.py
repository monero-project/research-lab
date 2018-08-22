# Dumb25519: a stupid implementation of ed25519
#
# Use this code only for prototyping
# -- putting this code into production would be dumb
# -- assuming this code is secure would also be dumb

import random
import hashlib

# curve parameters
b = 256
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493

# Useful helper methods
def exponent(b,e,m):
    return pow(b,e,m)

def invert(x,n):
    return exponent(x,n-2,n)

def xfromy(y):
    temp = (y*y-1) * invert(d*y*y+1,q)
    x = exponent(temp,(q+3)/8,q)
    if (x*x - temp) % q != 0:
        x = (x*I) % q
    if x % 2 != 0:
        x = q-x
    return x

d = -121665 * invert(121666,q)
I = exponent(2,(q-1)/4,q)

class Scalar:
    def __init__(self,x):
        self.x = x % l

    def invert(self):
        if self.x == 0:
            raise ZeroDivisionError
        return Scalar(invert(self.x,l))

    def __add__(self,y):
        if not isinstance(y,Scalar):
            raise TypeError
        return Scalar(self.x + y.x)

    def __sub__(self,y):
        if not isinstance(y,Scalar):
            raise TypeError
        return Scalar(self.x - y.x)

    def __mul__(self,y):
        if not isinstance(y,Scalar):
            raise TypeError
        return Scalar(self.x*y.x)

    def __div__(self,y):
        if not isinstance(y,Scalar):
            raise TypeError
        return Scalar(int(self.x/y.x))

    def __pow__(self,y):
        result = Scalar(1)
        for i in range(y):
            result = result*self
        return result

    def __eq__(self,y):
        if not isinstance(y,Scalar):
            raise TypeError
        return self.x == y.x

    def __ne__(self,y):
        if not isinstance(y,Scalar):
            raise TypeError
        return self.x != y.x

    def __lt__(self,y):
        if isinstance(y,Scalar):
            return self.x < y.x
        else:
            return self.x < y

    def __gt__(self,y):
        if isinstance(y,Scalar):
            return self.x > y.x
        else:
            return self.x > y

    def __str__(self):
        return str(self.x)

    def to_int(self):
        return self.x

class Point:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __eq__(self,Q):
        if not isinstance(Q,Point):
            raise TypeError
        return self.x == Q.x and self.y == Q.y

    def __ne__(self,Q):
        if not isinstance(Q,Point):
            raise TypeError
        return self.x != Q.x or self.y != Q.y

    def __add__(self,Q):
        if not isinstance(Q,Point):
            raise TypeError
        x1 = self.x
        y1 = self.y
        x2 = Q.x
        y2 = Q.y
        x3 = (x1*y2+x2*y1) * invert(1+d*x1*x2*y1*y2,q)
        y3 = (y1*y2+x1*x2) * invert(1-d*x1*x2*y1*y2,q)
        return Point(x3 % q, y3 % q)

    def __sub__(self,Q):
        if not isinstance(Q,Point):
            raise TypeError
        x1 = self.x
        y1 = self.y
        x2 = -Q.x
        y2 = Q.y
        x3 = (x1*y2+x2*y1) * invert(1+d*x1*x2*y1*y2,q)
        y3 = (y1*y2+x1*x2) * invert(1-d*x1*x2*y1*y2,q)
        return Point(x3 % q, y3 % q)

    def __mul__(self,y):
        if not isinstance(y,Scalar):
            raise TypeError
        if y == Scalar(0):
            return Point(0,1)
        Q = self.__mul__(y/Scalar(2))
        Q = Q.__add__(Q)
        if y.x & 1:
            Q = self.__add__(Q)
        return Q

    def __str__(self):
        return str(self.x) + str(self.y)

    def on_curve(self):
        x = self.x
        y = self.y
        return (-x*x + y*y - 1 - d*x*x*y*y) % q == 0

# make a point from a given integer y (if it is on the curve)
def make_point(y):
    x = xfromy(y)
    P = Point(x,y)
    if not P.on_curve():
        return None
    return P

# hash data to get a point on the curve in the G subgroup
def hash_to_point(data):
    while True:
        data = hashlib.sha256(data).hexdigest()
        if make_point(int(data,16)) is not None:
            return make_point(int(data,16))*Scalar(8)

# hash data to get a scalar
def hash_to_scalar(data):
    return Scalar(int(hashlib.sha256(data).hexdigest(),16))

# generate a random scalar
def random_scalar():
    return Scalar(random.randrange(0,l))

# generate a random point in the G subgroup
def random_point():
    return hash_to_point(str(random.random()))

# basepoint
Gy = 4*invert(5,q)
Gx = xfromy(Gy)
G = Point(Gx % q, Gy % q)

# zero point
Z = Point(0,1)

# a few more
H = hash_to_point('dumb25519 H')
T = hash_to_point('dumb25519 T')

# helper function to recursively flatten an ugly list
def flatten(L):
    if L == []:
        return L
    if isinstance(L[0],list):
        return flatten(L[0]) + flatten(L[1:])
    return L[:1] + flatten(L[1:])

# Pedersen vector commitment
def pedersen_commit(v,r):
    result = H*r
    for i in range(len(v)):
        result += hash_to_point('dumb25519 Gi'+str(i))*v[i]
    return result
