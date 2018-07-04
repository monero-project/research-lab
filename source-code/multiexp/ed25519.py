import random

# curve parameters
b = 256
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493

# op counts
counts = {}

def reset():
    counts['add'] = 0
    counts['multiply'] = 0
    
# compute b^e mod m
#def exponent(b,e,m):
#    if e == 0:
#        return 1
#    temp = exponent(b,e/2,m)**2 % m
#    if e & 1:
#        temp = (temp*b) % m
#    return temp
def exponent(b,e,m):
    return pow(b,e,m)

# compute x^(-1) mod m
def invert(x):
    return exponent(x,q-2,q)

# useful constants
d = -121665 * invert(121666)
I = exponent(2,(q-1)/4,q)

# given a y value, recover the x value on the curve
def xfromy(y):
    temp = (y*y-1) * invert(d*y*y+1)
    x = exponent(temp,(q+3)/8,q)
    if (x*x - temp) % q != 0:
        x = (x*I) % q
    if x % 2 != 0:
        x = q-x
    return x

# common basepoint (requires earlier function)
Gy = 4*invert(5)
Gx = xfromy(Gy)
G = [Gx % q, Gy % q]

# zero point
Z = [0,1]

# add P+Q
def _add(P,Q):
    x1 = P[0]
    y1 = P[1]
    x2 = Q[0]
    y2 = Q[1]
    x3 = (x1*y2+x2*y1) * invert(1+d*x1*x2*y1*y2)
    y3 = (y1*y2+x1*x2) * invert(1-d*x1*x2*y1*y2)
    return [x3 % q, y3 % q]

def add(P,Q):
    counts['add'] += 1
    return _add(P,Q)

# scalar multiply a*P
def _multiply(a,P):
    if a == 0:
        return [0,1]
    Q = _multiply(a/2,P)
    Q = _add(Q,Q)
    if a & 1:
        Q = _add(Q,P)
    return Q

def multiply(a,P):
    counts['multiply'] += 1
    return _multiply(a,P)

# generate a random scalar
def random_scalar():
    return random.randrange(0,l)

# generate a random multiple of the basepoint
def random_point():
    return _multiply(random_scalar(),G)
