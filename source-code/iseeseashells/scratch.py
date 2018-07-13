from hashlib import blake2s
import math
import random
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

# Ranges for randomly generated parameters

# initial spatial magnitude
initParamMin = float(2**-5)
initParamMax = float(1+2**-2)
deltaInit = (initParamMax - initParamMin)/256.0

# growth of spatial magnitude
growthParamMin = 1.0 - float(2**-5)
growthParamMax = 1.0 + float(2**-5)
deltaGrowth = (growthParamMax - growthParamMin)/256.0

# number of revolutions
revParamMin = 1
revParamMax = 4
deltaRev = (float(revParamMax) - float(revParamMin))/256.0

def getBlakeParams(inputAddress):
    # Compute H(inputAddress || H(inputAddress))
    h = blake2s()
    h.update(inputAddress.encode("utf-8"))
    d = str(h.digest()).encode("utf-8")
    h.update(d)

    # Regard h.digest as a sequence of bytes [0, ..., 255]
    d = h.digest()

    params = {}

    xInit = float(d[0])*deltaInit + initParamMin
    params.update({"xInit":xInit})

    xGrowth = float(d[1])*deltaGrowth + growthParamMin
    params.update({"xGrowth":xGrowth})

    yInit = float(d[2])*deltaInit + initParamMin
    params.update({"yInit":yInit})

    yGrowth = float(d[3])*deltaGrowth + growthParamMin
    params.update({"yGrowth":yGrowth})

    zInit = float(d[4]) * deltaInit + initParamMin
    params.update({"zInit": zInit})

    zGrowth = float(d[5]) * deltaGrowth + growthParamMin
    params.update({"zGrowth": zGrowth})

    rInit = float(d[6]) * deltaInit + initParamMin
    params.update({"rInit": rInit})

    rGrowth = float(d[7]) * deltaGrowth + growthParamMin
    params.update({"rGrowth": rGrowth})

    aInit = float(d[8]) * deltaInit + initParamMin
    params.update({"aInit": aInit})

    bInit = float(d[9]) * deltaInit + initParamMin
    params.update({"bInit": bInit})

    abGrowth = float(d[10]) * deltaGrowth + growthParamMin
    params.update({"abGrowth": abGrowth})

    revs = float(d[11]) * deltaRev + revParamMin
    params.update({"revs": revs})

    return params

def getFunctions(inputAddress):
    params = getBlakeParams(inputAddress)
    deltaT = params["revs"] / 256.0
    sx = 2*int(params["xInit"] > 0) - 1
    if params["xInit"]==0:
        sx = 0

    # Note: theta does not depend on s in this model)
    theta  = lambda inp: inp[1] + sx * math.asin(params["yInit"] * (params["yGrowth"]) ** inp[1] / math.sqrt((params["xInit"] ** 2) * (params["xGrowth"]) ** (2 * inp[1]) + (params["yInit"] ** 2) * (params["yGrowth"]) ** (2*inp[1]))) + math.pi * float(1 - sx) / 2.0
    radius = lambda inp: params["rInit"] * (params["rGrowth"]) ** inp[1] + math.sqrt((params["xInit"] ** 2) * (params["xGrowth"]) ** (2 * inp[1]) + (params["yInit"] ** 2) * (params["yGrowth"]) ** (2 * inp[1])) + params["aInit"] * inp[0] * (params["abGrowth"] ** inp[1])
    zUpper = lambda inp: params["zInit"] * (params["zGrowth"]) ** inp[1] + params["bInit"] * (params["abGrowth"] ** inp[1]) * math.sqrt(1 - inp[0] ** 2)
    zLower = lambda inp: params["zInit"] * (params["zGrowth"]) ** inp[1] - params["bInit"] * (params["abGrowth"] ** inp[1]) * math.sqrt(1 - inp[0] ** 2)

    return params, theta, radius, zUpper, zLower

inputAddress = str(random.random())
params, theta, radius, zUpper, zLower = getFunctions(inputAddress)

U = np.linspace(-1.0, 1.0, 256)
V = np.linspace(0.0, params["revs"], 256)
X = []
Y = []
surf1 = []
surf2 = []
for i in range(len(U)):
    u = U[i]
    surf1.append([])
    X.append([])
    surf2.append([])
    Y.append([])
    for j in range(len(V)):
        v = V[j]
        zup = zUpper([u,v])
        zlo = zLower([u,v])
        t = theta([u,v])
        r = radius([u,v])
        x = r*math.cos(t)
        y = r*math.sin(t)
        X[-1].append(x)
        Y[-1].append(y)
        surf1[-1].append(zup)
        surf2[-1].append(zlo)

X = np.array(X)
Y = np.array(Y)
surf1 = np.array(surf1)
surf2 = np.array(surf2)

fig = plt.figure()
ax = fig.gca(projection='3d')

# Plot the surface with face colors taken from the array we made.
surf = ax.plot_surface(X, Y, surf1)
plt.hold()
ssurf = ax.plot_surface(X,Y, surf2)
plt.show()