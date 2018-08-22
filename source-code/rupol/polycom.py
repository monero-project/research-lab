# RuPol: a dumb implementation of a draft ring confidential transaction scheme
#
# Use this code only for prototyping
# -- putting this code into production would be dumb
# -- assuming this code is secure would also be dumb

import dumb25519

# Commit to a polynomial h(X) of degree N = mn + d
# INPUT: list of N Scalar coefficients, m, n, d
# OUTPUT: message, state
def commit(h,m,n,d):
    if len(h) != m*n+d+1:
        raise ArithmeticError
    if m < 1 or n < 1 or d < 0 or d >= m:
        raise IndexError

    b = [dumb25519.random_scalar() for j in range(n)] + [dumb25519.Scalar(0)]  # blinding terms
    M = [] # blinded coefficient matrix; initially we define using columns

    # the first column is unique
    M.append([h[i] for i in range(d)] + [h[d]-b[0]] + [dumb25519.Scalar(0) for i in range(m-d)])

    # the rest of the columns (this is why there is an extra blinding term)
    for j in range(n):
        M.append([b[j]] + [h[i] for i in range(j*m+d+1,(j+1)*m+d)] + [h[(j+1)*m+d]-b[j+1]])

    # test that each matrix entry is a Scalar
    for i in range(n+1):
        for j in range(m+1):
            assert isinstance(M[i][j],dumb25519.Scalar)

    # commit to each row
    r = [dumb25519.random_scalar() for i in range(m+1)] # masks
    H = [] # commitments
    for i in range(m+1):
        H.append(dumb25519.pedersen_commit([col[i] for col in M],r[i]))

    return H,[M,b,r]

# Evaluate a committed polynomial at a given point
# INPUT: state, challenge point
# OUTPUT: message
def evaluate(state,x):
    if not isinstance(x,dumb25519.Scalar):
        raise TypeError

    M = state[0]
    r = state[2]

    hbar = []

    n = len(M) - 1
    m = len(M[0]) - 1
    for j in range(n+1):
        temp = dumb25519.Scalar(0)
        for i in range(m+1):
            temp += M[j][i]*(x**i)
        hbar.append(temp)

    rbar = dumb25519.Scalar(0)
    for i in range(m+1):
        rbar += r[i]*(x**i)

    return [hbar,rbar]

# Verify the evaluation of a committed polynomial
# INPUT: commit message, evaluation message, challenge point, size parameters
# OUTPUT: evaluation (or exception if verification fails)
def verify(msg1,msg2,x,m,n,d):
    H = msg1
    hbar = msg2[0]
    rbar = msg2[1]

    c = dumb25519.Z
    for i in range(len(H)):
        c += H[i]*(x**i)

    if dumb25519.pedersen_commit(hbar,rbar) != c:
        raise Exception('Failed polynomial commitment verification!')
    
    result = hbar[0]
    for j in range(1,n+1):
        result += hbar[j]*(x**((j-1)*m+d))
    return result
