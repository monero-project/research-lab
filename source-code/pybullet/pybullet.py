import dumb25519
from dumb25519 import Scalar, Point, ScalarVector, PointVector, random_scalar, random_point, hash_to_scalar, hash_to_point

cache = '' # rolling transcript hash

def mash(s):
    global cache
    cache = hash_to_scalar(str(cache) + str(s))

def scalar_to_bits(s,N):
    result = []
    for i in range(N-1,-1,-1):
        if s/Scalar(2**i) == Scalar(0):
            result.append(Scalar(0))
        else:
            result.append(Scalar(1))
            s -= Scalar(2**i)
    return ScalarVector(list(reversed(result)))

# generate a vector of powers of a scalar
def exp_scalar(s,l):
    return ScalarVector([s**i for i in range(l)])

# perform an inner-product proof round
# G,H: PointVector
# U: Point
# a,b: ScalarVector
#
# returns: G',H',U,a',b',L,R
def inner_product(data):
    global cache

    G = data[0]
    H = data[1]
    U = data[2]
    a = data[3]
    b = data[4]

    n = len(G)
    if n == 1:
        return [a[0],b[0]]

    n /= 2
    cL = a[:n]**b[n:]
    cR = a[n:]**b[:n]
    L = G[n:]*a[:n] + H[:n]*b[n:] + U*cL
    R = G[:n]*a[n:] + H[n:]*b[:n] + U*cR

    mash(L)
    mash(R)
    x = cache

    G = (G[:n]*x.invert())*(G[n:]*x)
    H = (H[:n]*x)*(H[n:]*x.invert())

    a = a[:n]*x + a[n:]*x.invert()
    b = b[:n]*x.invert() + b[n:]*x
    
    return [G,H,U,a,b,L,R]

# generate a multi-output proof
def prove(data,N):
    M = len(data)

    # curve points
    G = dumb25519.G
    H = dumb25519.H
    Gi = PointVector([hash_to_point('pybullet Gi ' + str(i)) for i in range(M*N)])
    Hi = PointVector([hash_to_point('pybullet Hi ' + str(i)) for i in range(M*N)])

    # set amount commitments
    V = PointVector([])
    aL = ScalarVector([])
    for v,gamma in data:
        V.append(H*v + G*gamma)
        mash(V[-1])
        aL.extend(scalar_to_bits(v,N))

    # set bit arrays
    aR = ScalarVector([])
    for bit in aL.scalars:
        aR.append(Scalar(1)-bit)

    alpha = random_scalar()
    A = Gi*aL + Hi*aR + G*alpha

    sL = ScalarVector([random_scalar()]*(M*N))
    sR = ScalarVector([random_scalar()]*(M*N))
    rho = random_scalar()
    S = Gi*sL + Hi*sR + G*rho

    # get challenges
    mash(A)
    mash(S)
    y = cache
    mash('')
    z = cache

    # polynomial coefficients
    l0 = aL - ScalarVector([z]*(M*N))
    l1 = sL

    # ugly sum
    zeros_twos = []
    for i in range (M*N):
        zeros_twos.append(Scalar(0))
        for j in range(1,M+1):
            temp = Scalar(0)
            if i >= (j-1)*N and i < j*N:
                temp = Scalar(2)**(i-(j-1)*N)
            zeros_twos[-1] = zeros_twos[-1] + temp*(z**(i+j))
    
    # more polynomial coefficients
    r0 = aR + ScalarVector([z]*(M*N))
    r0 = r0*exp_scalar(y,M*N)
    r0 = r0 + ScalarVector(zeros_twos)
    r1 = exp_scalar(y,M*N)*sR

    # build the polynomials
    t0 = l0**r0
    t1 = l0**r1 + l1**r0
    t2 = l1**r1

    tau1 = random_scalar()
    tau2 = random_scalar()
    T1 = H*t1 + G*tau1
    T2 = H*t2 + G*tau2

    mash(T1)
    mash(T2)
    x = cache # challenge

    taux = tau1*x + tau2*(x**2)
    for j in range(1,M+1):
        gamma = data[j-1][1]
        taux += z**(i+j)*gamma
    mu = x*rho+alpha
    
    l = l0 + l1*x
    r = r0 + r1*x
    t = l**r

    mash(x)
    mash(taux)
    mash(mu)
    mash(t)

    x_ip = cache # challenge
    L = PointVector([])
    R = PointVector([])
   
    # initial inner product inputs
    data = [Gi,PointVector([Hi[i]*(y.invert()**i) for i in range(len(Hi))]),H*x_ip,l,r]
    while True:
        data = inner_product(data)

        # we have reached the end of the recursion
        if len(data) == 2:
            return [V,A,S,T1,T2,taux,mu,L,R,data[0],data[1],t]

        # we are not done yet
        L.append(data[-2])
        R.append(data[-1])
