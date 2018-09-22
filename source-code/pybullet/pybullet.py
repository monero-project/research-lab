import dumb25519
from dumb25519 import Scalar, Point, ScalarVector, PointVector, random_scalar, random_point, hash_to_scalar, hash_to_point

cache = '' # rolling transcript hash
inv8 = Scalar(8).invert()

def mash(s):
    global cache
    cache = hash_to_scalar(str(cache) + str(s))

def clear_cache():
    global cache
    cache = ''

# turn a scalar into a vector of bit scalars
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

# sum the powers of a scalar
def sum_scalar(s,l):
    r = Scalar(0)
    for i in range(l):
        r += s**i
    return r

# perform an inner-product proof round
# G,H: PointVector
# U: Point
# a,b: ScalarVector
#
# returns: G',H',U,a',b',L,R
def inner_product(data):
    G,H,U,a,b,L,R = data

    n = len(G)
    if n == 1:
        return [a[0],b[0]]

    n /= 2
    cL = a[:n]**b[n:]
    cR = a[n:]**b[:n]
    L = (G[n:]*a[:n] + H[:n]*b[n:] + U*cL)*inv8
    R = (G[:n]*a[n:] + H[n:]*b[:n] + U*cR)*inv8

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
    clear_cache()
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
        V.append((H*v + G*gamma)*inv8)
        mash(V[-1])
        aL.extend(scalar_to_bits(v,N))

    # set bit arrays
    aR = ScalarVector([])
    for bit in aL.scalars:
        aR.append(bit-Scalar(1))

    alpha = random_scalar()
    A = (Gi*aL + Hi*aR + G*alpha)*inv8

    sL = ScalarVector([random_scalar()]*(M*N))
    sR = ScalarVector([random_scalar()]*(M*N))
    rho = random_scalar()
    S = (Gi*sL + Hi*sR + G*rho)*inv8

    # get challenges
    mash(A)
    mash(S)
    y = cache
    y_inv = y.invert()
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
            zeros_twos[-1] += temp*(z**(1+j))
    
    # more polynomial coefficients
    r0 = aR + ScalarVector([z]*(M*N))
    r0 = r0*exp_scalar(y,M*N)
    r0 += ScalarVector(zeros_twos)
    r1 = exp_scalar(y,M*N)*sR

    # build the polynomials
    t0 = l0**r0
    t1 = l0**r1 + l1**r0
    t2 = l1**r1

    tau1 = random_scalar()
    tau2 = random_scalar()
    T1 = (H*t1 + G*tau1)*inv8
    T2 = (H*t2 + G*tau2)*inv8

    mash(T1)
    mash(T2)
    x = cache # challenge

    taux = tau1*x + tau2*(x**2)
    for j in range(1,M+1):
        gamma = data[j-1][1]
        taux += z**(1+j)*gamma
    mu = x*rho+alpha
    
    l = l0 + l1*x
    r = r0 + r1*x
    t = l**r

    mash(taux)
    mash(mu)
    mash(t)

    x_ip = cache # challenge
    L = PointVector([])
    R = PointVector([])
   
    # initial inner product inputs
    data_ip = [Gi,PointVector([Hi[i]*(y_inv**i) for i in range(len(Hi))]),H*x_ip,l,r,None,None]
    while True:
        data_ip = inner_product(data_ip)

        # we have reached the end of the recursion
        if len(data_ip) == 2:
            return [V,A,S,T1,T2,taux,mu,L,R,data_ip[0],data_ip[1],t]

        # we are not done yet
        L.append(data_ip[-2])
        R.append(data_ip[-1])

# verify a batch of multi-output proofs
def verify(proofs,N):
    # determine the length of the longest proof
    max_MN = 2**max([len(proof[7]) for proof in proofs])

    # curve points
    Z = dumb25519.Z
    G = dumb25519.G
    H = dumb25519.H
    Gi = PointVector([hash_to_point('pybullet Gi ' + str(i)) for i in range(max_MN)])
    Hi = PointVector([hash_to_point('pybullet Hi ' + str(i)) for i in range(max_MN)])

    # set up weighted aggregates
    y0 = Scalar(0)
    y1 = Scalar(0)
    z1 = Scalar(0)
    z3 = Scalar(0)
    z4 = [Scalar(0)]*max_MN
    z5 = [Scalar(0)]*max_MN
    BigAssMultiexp = []

    # run through each proof
    for proof in proofs:
        clear_cache()

        V,A,S,T1,T2,taux,mu,L,R,a,b,t = proof

        # get size information
        M = 2**len(L)/N

        # weighting factors for batching
        weight_y = random_scalar()
        weight_z = random_scalar()
        if weight_y == Scalar(0) or weight_z == Scalar(0):
            raise ArithmeticError

        # reconstruct all challenges
        for v in V:
            mash(v)
        mash(A)
        mash(S)
        if cache == Scalar(0):
            raise ArithmeticError
        y = cache
        y_inv = y.invert()
        mash('')
        if cache == Scalar(0):
            raise ArithmeticError
        z = cache
        mash(T1)
        mash(T2)
        if cache == Scalar(0):
            raise ArithmeticError
        x = cache
        mash(taux)
        mash(mu)
        mash(t)
        if cache == Scalar(0):
            raise ArithmeticError
        x_ip = cache

        y0 += taux*weight_y
        
        k = (z-z**2)*sum_scalar(y,M*N)
        for j in range(1,M+1):
            k -= (z**(j+2))*sum_scalar(Scalar(2),N)

        y1 += (t-k)*weight_y

        for j in range(M):
            BigAssMultiexp.append([V[j]*Scalar(8),z**(j+2)*weight_y])
        BigAssMultiexp.append([T1*Scalar(8),x*weight_y])
        BigAssMultiexp.append([T2*Scalar(8),x**2*weight_y])

        BigAssMultiexp.append([A*Scalar(8),weight_z])
        BigAssMultiexp.append([S*Scalar(8),x*weight_z])

        # inner product
        W = ScalarVector([])
        for i in range(len(L)):
            mash(L[i])
            mash(R[i])
            if cache == Scalar(0):
                raise ArithmeticError
            W.append(cache)
        W_inv = W.invert()

        for i in range(M*N):
            index = i
            g = a
            h = b*((y_inv)**i)
            for j in range(len(L)-1,-1,-1):
                J = len(W)-j-1
                base_power = 2**j
                if index/base_power == 0:
                    g *= W_inv[J]
                    h *= W[J]
                else:
                    g *= W[J]
                    h *= W_inv[J]
                    index -= base_power

            g += z
            h -= (z*(y**i) + (z**(2+i/N))*(Scalar(2)**(i%N)))*((y_inv)**i)

            z4[i] += g*weight_z
            z5[i] += h*weight_z

        z1 += mu*weight_z

        for i in range(len(L)):
            BigAssMultiexp.append([L[i]*Scalar(8),(W[i]**2)*weight_z])
            BigAssMultiexp.append([R[i]*Scalar(8),(W_inv[i]**2)*weight_z])
        z3 += (t-a*b)*x_ip*weight_z
    
    # now check all proofs together
    BigAssMultiexp.append([G,-y0-z1])
    BigAssMultiexp.append([H,-y1+z3])
    for i in range(max_MN):
        BigAssMultiexp.append([Gi[i],-z4[i]])
        BigAssMultiexp.append([Hi[i],-z5[i]])

    if not dumb25519.multiexp(BigAssMultiexp) == Z:
        raise ArithmeticError('Bad z check!')

    return True
