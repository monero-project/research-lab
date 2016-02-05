import Crypto.Random.random as rand
import itertools
import math #for log
import sys
def decomposition(i):
    #from stack exchange, don't think it's uniform
    while i > 0:
        n = rand.randint(1, i)
        yield n
        i -= n

def Decomposition(i):
    while True:
        l = list(decomposition(i))
        if len(set(l)) == len(l):
            return l

def decomposition2(n, s, d, k):
    #home-brewed, returns no duplicates, includes the number d
    s = s - 1
    n = n
    while True:
        a = [d]
        nn = n
        #a.append(d)
        for i in range(0, s):
            a.append(rand.randint(0, n))
        a.sort()
        #print("a", a)
        b = []
        c = []
        while len(a) > 0:
            t = a.pop()
            #print(t, a)
            if t >= d:
                b.append(nn - t)
            else:
                c.append(nn - t)
            nn = t
        c.append(nn)
        tot = b[:] + c[:]
        #print("b", b)
        if sum(set(tot)) == n and len(c) > int(k):
            return sorted(c), sorted(b)

def decomposition3(n, s, d, k):
    #a combination of both methods, designed to get some smaller values
    send, change = decomposition2(n, s, d, k)
    for i in send:
        if i > n / s:
            send.remove(i)
            send = send + list(Decomposition(i))
    for i in change:
        if i > n / (s - 1):
            change.remove(i)
            change = change + list(Decomposition(i))
    return send, change

def divv(l, m):
    return [a /float( m) for a in l]

def frexp10(x): 
    exp = int(math.log10(x)) 
    return x / 10**exp, exp 


def decideAmounts(totalInputs, toSend, Partitions, k, fuzz):
    #fuzz is an optional amount to fuzz the transaction by
    #so if you start with a big obvious number like 2000, it might be fuzzed by up to "fuzz" amount
    fz = rand.randint(0, int(fuzz * 1000) ) / 1000.0
    toSend += fz


    g, ii =frexp10(totalInputs)
    ii = 10 ** (-1 * min(ii - 2, 0))
    print("ii", ii)
    M = 10 ** (int(math.log(2 ** Partitions) / math.log(10))) * ii
    #M = 10 ** M
    print("multiplier:", M)
    totalInputs = int(totalInputs *  M)
    toSend = int(toSend * M)
    change = totalInputs - toSend
    send_amounts, change_amounts = decomposition3(totalInputs, Partitions, toSend, k)
    all_amounts = send_amounts[:] + change_amounts[:]
    rand.shuffle(all_amounts)
    print("")
    print("change amounts:", divv(change_amounts, M))
    print("send amounts:", divv(send_amounts, M))
    print("now from the following, how much is sent?")
    print("all amounts:", sorted(divv(all_amounts, M)))
    print("possible sent amounts:")
    amounts = []
    for L in range(0, len(all_amounts)+1):
        for subset in itertools.combinations(all_amounts, L):
            amounts.append(sum(subset))

    print("number of possible sent amounts:")
    print(len(amounts))
    print("2^N:", 2 ** len(all_amounts))
    print("number of possible sent amounts duplicates removed:")
    print(len(list(set(amounts))))



if len(sys.argv) > 2:
    kk = 2
    parts = 7
    kk = rand.randint(1, int(parts / 4)) #how many sends to demand
    fuzz = 1
    decideAmounts(float(sys.argv[1]), float(sys.argv[2]), parts, kk, fuzz)
