from hashlib import blake2b
import math
import random
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

# Some global parameters
# Further fine-tuning of these will improve shell quality.
minFloatParam = 2.0**-1
maxFloatParam = 2.0**2
minFrequency = 2.0**-3
maxFrequency = 2.0**3
maxGrowthRate = 5.0**(1.0/256.0) - 1.0
maxHeightDrift = 2.0**15

# We model a shell by:
#  1) Take the parameterization of an ellipse embedded in the (r,z) plane in cylindrical coordinates
#        t = t, r = a*cos(s), z = b*cos(s) for parameter s on [0, 2*pi)
#  2) We rotate the ellipse as t varies with frequency frequencyOne.
#        t = t, (r', z') = ((cos(frequencyOne*t), -sin(frequencyOne*t)), (sin(frequencyOne*t), cos(frequencyOne*t)))*(r,z)
#  3) We translate the ellipse so it is centered on a logarithmic spiral with a linear height shift:
#        t = t, r = init_radius*math.exp(growthRate*t), z = init_height*math.exp(growthRate*t) + height_slope*t
#  4) We take parameter t on [0, 2*pi*R) to get R revolutions around the central axis, and we take the parameter
#     s on [0, 2*pi) to compute the cross section of the shell at angle theta = t. Resulting in surface consisting of
#     points (t, r, z) parameterized by (t, s) by the following system of equations where we denote all parameters as
#     occurring in the list par.
#        t : = t
#        r := ((par[0]*math.cos(par[1]*t)*math.cos(s) - par[2]*math.sin(par[1]*t)*math.sin(s))*(1.0 + par[3]*math.cos(par[4]*s) + par[5]*math.sin(par[4]*s)) - par[6])*math.exp(par[7]*t)
#        z := ((par[0]*math.sin(par[1]*t)*math.cos(s) + par[2]*math.cos(par[1]*t)*math.sin(s))*(1.0 + par[3]*math.cos(par[4]*s) + par[5]*math.sin(par[4]*s)) - par[8])*math.exp(par[7]*t) + par[9]*t
#
# We find the parameters describing the shell by:
#  1) Computing a 64-byte hash digest of the address.
#  2) Parse the digest 4 bytes at a time.
#  3) Each 4-byte block is used in the following way:
#         0:3   :  ellipse-semi-axis-one measure
#         4:7   :  ellipse-semi-axis-two measure
#         8:11  :  ellipse spin frequency
#         12:15 :  shell ridge frequency
#         16:19 :  shell ridge measure one
#         20:23 :  shell ridge measure two
#         24:27 :  radial measure
#         28:31 :  height measure
#         32:35 :  growth rate
#         36:39 :  vertical drift speed

def getBlakeDigests(inputAddress):
    ''' Take as input some inputAddress and produce as output a hash digest. Not quite an HMAC.'''
    h = blake2b()
    h.update(str("iseeseashells").encode("utf-8"))
    tempOne = str(h.digest())

    h = blake2b()
    h.update(str("downbytheseashore").encode("utf-8"))
    tempTwo = str(h.digest())

    h = blake2b()
    h.update(tempOne.encode("utf-8"))
    h.update(inputAddress.encode("utf-8"))
    tempThree = str(h.digest())

    h = blake2b()
    h.update(tempTwo.encode("utf-8"))
    h.update(tempThree.encode("utf-8"))
    d = h.digest()
    return d

def getParams(d):
    ''' Take as input a hash digest, interprets it bytewise as integers, returns params. '''
    params = {"semiAxisOneInit": None, "frequencyOne": None, "wobbleOne": None, "frequencyTwo": None, "wobbleTwo": None,
              "semiAxisTwoInit": None, "radiusInit": None, "heightInit":None, "growth": None, "heightChangeConst":None}

    # Ellipse-semi-axis-one initial spatial parameter.
    # Drawn from minFloatParam to maxFloatParam
    next = d[:4]
    nextInt = int.from_bytes(next, byteorder='big')
    nextFloat = float(nextInt)*(2.0**-32)
    assert 0.0 <= nextFloat
    assert nextFloat < 1.0
    nextParam = minFloatParam + (maxFloatParam - minFloatParam)*nextFloat
    params.update({"semiAxisOneInit":nextParam}) # float, [minFloatParam, maxFloatParam)

    # Ellipse-semi-axis-two initial spatial parameter.
    # Drawn from minFloatParam to maxFloatParam
    next = d[4:8]
    nextInt = int.from_bytes(next, byteorder='big')
    nextFloat = float(nextInt)*(2.0**-32)
    assert 0.0 <= nextFloat
    assert nextFloat < 1.0
    nextParam = minFloatParam + (maxFloatParam - minFloatParam)*nextFloat
    params.update({"semiAxisTwoInit":nextParam}) # float, [maxFloatParam, maxFloatParam)

    # Spatial frequency at which the ellipse spins its orientation.
    # Drawn from minFrequency to maxFrequency
    next = d[8:12]
    nextInt = int.from_bytes(next, byteorder='big')
    nextFloat = float(nextInt)*(2.0**-32)
    assert 0.0 <= nextFloat
    assert nextFloat < 1.0
    nextParam = minFrequency + (maxFrequency - minFrequency)*nextFloat
    params.update({"frequencyOne":nextParam}) # float, [minFrequency, maxFrequency)

    # Spatial requency at which the cross section of the shell wobbles/shell ridges
    # Drawn from minFrequency to maxFrequency
    next = d[12:16]
    nextInt = int.from_bytes(next, byteorder='big')
    nextFloat = float(nextInt)*(2.0**-32)
    assert 0.0 <= nextFloat
    assert nextFloat < 1.0
    nextParam = minFrequency + (maxFrequency - minFrequency)*nextFloat
    params.update({"frequencyTwo":nextParam}) # float, [maxFrequency, maxFrequency)

    # Relative spatial amount of wobble along first semi-axis
    # Drawn from -1.0 to 1.0
    next = d[16:20]
    nextInt = int.from_bytes(next, byteorder='big')
    nextFloat = 2.0*float(nextInt)*(2.0**-32) - 1.0
    assert -1.0 <= nextFloat
    assert nextFloat < 1.0
    nextParam = nextFloat
    params.update({"wobbleOne":nextFloat}) # float, (-1, 1)

    # Relative spatial amount of wobble along second semi-axis
    # Drawn from -1.0*math.sqrt(1.0 - wobbleOne**2) to 1.0*math.sqrt(1.0 - wobbleOne**2)
    next = d[20:24]
    nextInt = int.from_bytes(next, byteorder='big')
    nextFloat = 2.0*float(nextInt)*(2.0**-32) - 1.0
    assert -1.0 <= nextFloat
    assert nextFloat < 1.0
    nextParam = math.sqrt(1.0 - params["wobbleOne"]**2)*nextFloat
    params.update({"wobbleTwo":nextParam}) # float, (-1+sqrt(1-wobbleOne**2), 1-sqrt(1-wobbleOne**2))

    # Initial radius spatial parameter (determines centerline of logarithmic spiral)
    # Drawn from minFloatParam to maxFloatParam
    next = d[24:28]
    nextInt = int.from_bytes(next, byteorder='big')
    nextFloat = float(nextInt)*(2.0**-32)
    assert 0.0 <= nextFloat
    assert nextFloat < 1.0
    nextParam = minFloatParam + (maxFloatParam - minFloatParam)*nextFloat
    params.update({"radiusInit":nextParam}) # float, [minFloatParam, maxFloatParam)

    # Initial height spatial parameter (determines centerline of logarithmic spiral)
    # Drawn from minFloatParam to maxFloatParam
    next = d[28:32]
    nextInt = int.from_bytes(next, byteorder='big')
    nextFloat = float(nextInt)*(2.0**-32)
    assert 0.0 <= nextFloat
    assert nextFloat < 1.0
    nextParam = minFloatParam + (maxFloatParam - minFloatParam)*nextFloat
    params.update({"heightInit":nextParam}) # float, [minFloatParam, maxFloatParam)

    # Logarithmic growth rate.
    # Drawn from 1.0/(1.0 + maxGrowthRate) to 1.0 + maxGrowthRate
    # Different growth rate for different things can lead to ugly seashells...
    # but having more parameters squeezed out of an address hash means the result
    # is less likely to produce a convincing visual near-duplicate... so
    # TODO: different growth rates for different things?
    # Can work but only if we restrict our random parameter generation to "pretty" subspaces.
    next = d[32:36]
    nextInt = int.from_bytes(next, byteorder='big')
    nextFloat = 2.0*float(nextInt)*(2.0**-32) - 1.0
    assert -1.0 <= nextFloat
    assert nextFloat < 1.0
    nextParam = (1.0 + maxGrowthRate)**nextFloat
    params.update({"growth":nextParam}) # float, [1.0/maxGrowthRate, maxGrowthRate)

    # Constant drift of height. If this is large, then you get a long cone-shaped shell.
    # If this is small, you get a clam.
    # Drawn from 0.0 to maxHeightDrift
    next = d[36:40]
    nextInt = int.from_bytes(next, byteorder='big')
    nextFloat = float(nextInt)*(2.0**-32)
    assert 0.0 <= nextFloat
    assert nextFloat < 1.0
    nextParam = nextFloat*maxHeightDrift
    params.update({"heightChangeConst":nextParam}) # float, [1.0/maxGrowthRate, maxGrowthRate)

    return params

def getFunctions(inputAddress):
    ''' Takes as input some inputAddress, computes params, and returns params with some ambda functions describing
        the parameterization of the resulting shell. '''
    d = getBlakeDigests(inputAddress)
    params = getParams(d)
    theta = lambda inp:inp[0]
    radius = lambda inp:((params["semiAxisOneInit"]*math.cos(params["frequencyOne"]*inp[0])*math.cos(inp[1])*(1.0+params["wobbleOne"]*math.cos(params["frequencyTwo"]*inp[1]) + params["wobbleTwo"]*math.sin(params["frequencyTwo"]*inp[1])) - params["semiAxisTwoInit"]*math.sin(params["frequencyOne"]*inp[0])*math.sin(inp[1])*(1.0+params["wobbleOne"]*math.cos(params["frequencyTwo"]*inp[1]) + params["wobbleTwo"]*math.sin(params["frequencyTwo"]*inp[1])) - params["radiusInit"])*math.exp(params["growth"]*inp[0]))
    height = lambda inp:(params["heightChangeConst"]*inp[0] + ((params["semiAxisOneInit"]*math.sin(params["frequencyOne"]*inp[0])*math.cos(inp[1])*(1.0+params["wobbleOne"]*math.cos(params["frequencyTwo"]*inp[1]) + params["wobbleTwo"]*math.sin(params["frequencyTwo"]*inp[1])) + params["semiAxisTwoInit"]*math.cos(params["frequencyOne"]*inp[0])*math.sin(inp[1])*(1.0+params["wobbleOne"]*math.cos(params["frequencyTwo"]*inp[1]) + params["wobbleTwo"]*math.sin(params["frequencyTwo"]*inp[1])) - params["heightInit"])*math.exp(params["growth"]*inp[0])))
    return params, theta, radius, height

def seeseashell(inputAddress):
    ''' Takes as input some inputAddress, computes getFunctions, and plots the resulting shell.'''
    if type(inputAddress) != type(str(1)):
        inputAddress = str(inputAddress)
    params, theta, radius, height = getFunctions(inputAddress)

    U1 = np.linspace(0.0, math.pi, 256)
    U2 = np.linspace(math.pi, 2.0*math.pi, 256)
    T = np.linspace(0.0, 2.0*math.pi*5.0, 256)
    X1 = []
    X2 = []
    Y1 = []
    Y2 = []
    surf1 = []
    surf2 = []
    for i in range(len(U1)):
        u1 = U1[i]
        u2 = U2[i]
        surf1.append([])
        X1.append([])
        X2.append([])
        surf2.append([])
        Y1.append([])
        Y2.append([])
        for j in range(len(T)):
            t = T[j]
            z1 = height([t,u1])
            z2 = height([t,u2])
            r1 = radius([t,u1])
            r2 = radius([t,u2])
            x1 = r1 * math.cos(t)
            x2 = r2 * math.cos(t)
            y1 = r1 * math.sin(t)
            y2 = r2 * math.sin(t)
            X1[-1].append(x1)
            X2[-1].append(x2)
            Y1[-1].append(y1)
            Y2[-1].append(y2)
            surf1[-1].append(z1)
            surf2[-1].append(z2)
    X1 = np.array(X1)
    X2 = np.array(X2)
    Y1 = np.array(Y1)
    Y2 = np.array(Y2)
    surf1 = np.array(surf1)
    surf2 = np.array(surf2)

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # Plot the surface with face colors taken from the array we made.
    surf = ax.plot_surface(X1, Y1, surf1)
    ssurf = ax.plot_surface(X2, Y2, surf2)

    print(params)
    plt.show()

seeseashell("1Qalkhd130947oeiqhroh" + str(random.random()))