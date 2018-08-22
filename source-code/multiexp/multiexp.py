# Each test computes an expression of the form a1*P1 + ... + an*Pn
# - each ai is a scalar
# - each Pi is a curve point

import ed25519
import heapq
from copy import deepcopy
from time import clock
import cPickle

MIN_POINTS = 2 # size of first trial
MAX_POINTS = 64 # size of last trial

# use individual operations
def basic(data):
    result = ed25519.Z # zero point
    for datum in data:
        result = ed25519.add(result,ed25519.multiply(datum[0],datum[1]))
    return result

# use Bos-Coster with linear search
def boscoster(data):
    while True:
        index1 = 0
        for i in range(len(data)):
            if data[i][0] > data[index1][0]:
                index1 = i
        index2 = 0
        if index2 == index1:
            index2 = 1
        for i in range(len(data)):
            if i != index1:
                if data[i][0] > data[index2][0]:
                    index2 = i
        if data[index2][0] == 0:
            return ed25519.multiply(data[index1][0],data[index1][1])
        data[index2][1] = ed25519.add(data[index2][1],data[index1][1])
        data[index1][0] = (data[index1][0] - data[index2][0]) % ed25519.l # scalar subtraction

# use Bos-Coster with linear search and pathological input fix
def boscoster_robust(data):
    while True:
        index1 = 0
        for i in range(len(data)):
            if data[i][0] > data[index1][0]:
                index1 = i
        index2 = 0
        if index2 == index1:
            index2 = 1
        for i in range(len(data)):
            if i != index1:
                if data[i][0] > data[index2][0]:
                    index2 = i
        if data[index2][0] == 0:
            return ed25519.multiply(data[index1][0],data[index1][1])

        # handle pathological inputs where s1 > 2s2
        # replace (s1,P1) with (s1/2,2*P1)
        while data[index1][0] > 2*data[index2][0]:
            # if s1 is odd, add (1,P1) at the end of the heap
            if (data[index1][0] % 2) == 1:
                data.append([1,data[index1][1]])
            data[index1][0] = long(data[index1][0]/2)
            data[index1][1] = ed25519.add(data[index1][1],data[index1][1])

        data[index2][1] = ed25519.add(data[index2][1],data[index1][1])
        data[index1][0] = (data[index1][0] - data[index2][0]) % ed25519.l # scalar subtraction

# use Bos-Coster with linear search and pathological input fix, with sum aggregation
def boscoster_robust2(data):
    while True:
        index1 = 0
        for i in range(len(data)):
            if data[i][0] > data[index1][0]:
                index1 = i
        index2 = 0
        if index2 == index1:
            index2 = 1
        for i in range(len(data)):
            if i != index1:
                if data[i][0] > data[index2][0]:
                    index2 = i
        if data[index2][0] == 0:
            return ed25519.multiply(data[index1][0],data[index1][1])

        # handle pathological inputs where s1 > 2s2
        # replace (s1,P1) with (s1/2,2*P1)
        tail_point = ed25519.Z # handles odd scalars
        while data[index1][0] > 2*data[index2][0]:
            # if s1 is odd, add (1,P1) at the end of the heap
            if (data[index1][0] % 2) == 1:
                tail_point = ed25519.add(tail_point,data[index1][1])
            data[index1][0] = long(data[index1][0]/2)
            data[index1][1] = ed25519.add(data[index1][1],data[index1][1])

        if tail_point != ed25519.Z:
            data.append([1,tail_point])
        data[index2][1] = ed25519.add(data[index2][1],data[index1][1])
        data[index1][0] = (data[index1][0] - data[index2][0]) % ed25519.l # scalar subtraction

# use Bos-Coster with a heap structure
def boscosterheap(data):
    data = [[-datum[0],datum[1]] for datum in data] # to form a descending heap
    heapq.heapify(data)
    while len(data) > 1:
        item1 = heapq.heappop(data)
        item2 = heapq.heappop(data)
        s1,p1 = -item1[0],item1[1]
        s2,p2 = -item2[0],item2[1]
        p2 = ed25519.add(p1,p2)
        s1 = (s1 - s2) % ed25519.l # scalar subtraction
        if s1 > 0L:
            heapq.heappush(data,[-s1,p1])
        heapq.heappush(data,[-s2,p2])
    result = heapq.heappop(data)
    return ed25519.multiply(-result[0],result[1])

# use Bos-Coster with a heap structure and pathological input fix
def boscosterheap_robust(data):
    data = [[-datum[0],datum[1]] for datum in data] # to form a descending heap
    heapq.heapify(data)
    while len(data) > 1:
        item1 = heapq.heappop(data)
        item2 = heapq.heappop(data)
        s1,p1 = -item1[0],item1[1]
        s2,p2 = -item2[0],item2[1]

        # handle pathological inputs where s1 > 2s2
        # replace (s1,P1) with (s1/2,2*P1)
        while s1 > 2*s2:
            # if s1 is odd, add (1,P1) at the end of the heap
            if (s1 % 2) == 1:
                heapq.heappush(data,[-1,p1])
            s1 = long(s1/2)
            p1 = ed25519.add(p1,p1)

        p2 = ed25519.add(p1,p2)
        s1 = (s1 - s2) % ed25519.l # scalar subtraction
        if s1 > 0L:
            heapq.heappush(data,[-s1,p1])
        heapq.heappush(data,[-s2,p2])
    result = heapq.heappop(data)
    return ed25519.multiply(-result[0],result[1])

# use Bos-Coster with a heap structure and pathological input fix, with sum aggregation
def boscosterheap_robust2(data):
    data = [[-datum[0],datum[1]] for datum in data] # to form a descending heap
    heapq.heapify(data)
    while len(data) > 1:
        item1 = heapq.heappop(data)
        item2 = heapq.heappop(data)
        s1,p1 = -item1[0],item1[1]
        s2,p2 = -item2[0],item2[1]

        # handle pathological inputs where s1 > 2s2
        # replace (s1,P1) with (s1/2,2*P1)
        tail_point = ed25519.Z # handles odd scalars
        while s1 > 2*s2:
            # if s1 is odd, add (1,P1) at the end of the heap
            if (s1 % 2) == 1:
                tail_point = ed25519.add(tail_point,p1)
            s1 = long(s1/2)
            p1 = ed25519.add(p1,p1)

        if tail_point != ed25519.Z:
            heapq.heappush(data,[-1,tail_point])
        p2 = ed25519.add(p1,p2)
        s1 = (s1 - s2) % ed25519.l # scalar subtraction
        if s1 > 0L:
            heapq.heappush(data,[-s1,p1])
        heapq.heappush(data,[-s2,p2])
    result = heapq.heappop(data)
    return ed25519.multiply(-result[0],result[1])

# use Straus
def straus(data):
    c = 4 # fixed window parameter
    scalars = [datum[0] for datum in data]
    points = [datum[1] for datum in data]
    multiples = [False,points]
    for i in range(2,2**c):
        multiples.append([ed25519.add(P,Q) for P,Q in zip(points,multiples[i-1])])
    maxscalar = max(scalars)
    i = 0
    while 2**i <= maxscalar:
        i += c
    result = ed25519.Z # zero point

    while i >= c:
        for j in range(c):
            result = ed25519.add(result,result)
            i -= 1
        for j in range(len(scalars)):
            digit = (scalars[j] >> i) % (2**c)
            if digit > 0:
                result = ed25519.add(result,multiples[digit][j])
    return result
    
# use Pippenger
def pippenger(data):
    scalars = [datum[0] for datum in data]
    points = [datum[1] for datum in data]
    buckets = None
    nonzero = False
    result = ed25519.Z # zero point
   
    c = 4 # window parameter; NOTE: the optimal value actually depends on len(points) empirically

    # really we want to use the max bitlength to compute groups
    maxscalar = max(scalars)
    groups = 0
    while maxscalar >= 2**groups:
        groups += 1
    groups = int((groups + c - 1) / c)
    
    # loop is really (groups-1)..0
    for k in range(groups-1,-1,-1):
        if result != ed25519.Z:
            for i in range(c):
                result = ed25519.add(result,result)
        
        buckets = [ed25519.Z]*(2**c) # clear all buckets
        
        # partition scalars into buckets
        for i in range(len(scalars)):
            bucket = 0
            for j in range(c):
                if scalars[i] & (1 << (k*c+j)): # test for bit
                    bucket |= 1 << j
            
            if bucket == 0: # zero bucket is never used
                continue
            
            if buckets[bucket] != ed25519.Z:
                buckets[bucket] = ed25519.add(buckets[bucket],points[i])
            else:
                buckets[bucket] = points[i]
        
        # sum the buckets
        pail = ed25519.Z
        for i in range(len(buckets)-1,0,-1):
            if buckets[i] != ed25519.Z:
                pail = ed25519.add(pail,buckets[i])
            if pail != ed25519.Z:
                result = ed25519.add(result,pail)
            
    return result
        
# Which tests should be run? 
# NOTE: the first test is used as the control to check correctness of the others
TESTS = [boscosterheap_robust2,straus,pippenger]

# Try to load existing points
data = None
try:
    data = cPickle.load(open('points.p','rb'))
    assert len(data) >= MAX_POINTS
    print 'Loaded',len(data),'points from file. Testing...'
except:
    print 'Generating',MAX_POINTS,'points...'
    data = [[ed25519.random_scalar(),ed25519.random_point()] for point in range(MAX_POINTS)]
    cPickle.dump(data,open('points.p','wb'))
    print 'Done. Testing...'

counter = MIN_POINTS

# For each test: determine correctness, time the operation, and count the number of point additions
print 'test points adds time'
while counter <= MAX_POINTS:
    result = None
    for test in TESTS:
        temp = deepcopy(data[:counter])
        start = clock()
        ed25519.reset() # op counts

        # use the initial operation to test correctness
        new_result = test(temp)
        if result is None:
            result = new_result
        else:
            if new_result != result:
                print "Failed test"

        stop = clock()
        print test.__name__,counter,ed25519.counts['add'],stop-start

    counter *= 2
