#see https://eprint.iacr.org/2015/1098.pdf
import MiniNero
import PaperWallet

def keyVector(rows):
    return [None] * rows

def keyImage(x, rows):
    HP = keyVector(rows)
    KeyImage = keyVector(rows)
    for i in range(0, rows):
      HP[i] = MiniNero.hashToPoint_cn(MiniNero.scalarmultBase(x[i]))
      KeyImage[i] = MiniNero.scalarmultKey(HP[i], x[i])
    return KeyImage

def MLSAG_Sign(pk, xx, index):
    rows = len(xx)
    cols = len(pk[0])
    print("Generating MLSAG sig of dimensions ",rows ,"x ", cols)
    L = [[None] * cols] #list of keyvectors? except it's indexed by cols... it's kind of internal actually
    R = [[None] * cols]
    s = [[PaperWallet.skGen() for i in range(0, cols)] ] #first index is rows, second is cols, wonder if I should switch that..
    HP = [[MiniNero.hashToPoint_cn(i) for i in pk[0]]]

    pj = ''.join(pk[0])  
    for i in range(1, rows):
      L.append([None] * cols)
      R.append([None] * cols)
      s.append([PaperWallet.skGen() for j in range(0, cols)])
      HP.append([MiniNero.hashToPoint_cn(j) for j in pk[i]]) 
      pj = pj + ''.join(pk[i])

    c= [None] * cols #1-dimensional
    keyimage = keyImage(xx, rows) #ok
    for i in range(0, rows):
      L[i][index] = MiniNero.scalarmultBase(s[i][index]) #aG
      R[i][index] = MiniNero.scalarmultKey(HP[i][index], s[i][index]) #aH
    j = (index + 1) % cols
    tohash = pj
    for i in range(0, rows):
      tohash = tohash + L[i][index] + R[i][index]
    c[j] = MiniNero.cn_fast_hash(tohash)
    while j != index:
      tohash = pj
      for i in range(0, rows):
        L[i][j] = MiniNero.addKeys(MiniNero.scalarmultBase(s[i][j]), MiniNero.scalarmultKey(pk[i][j], c[j])) #Lj = sG + cxG
        R[i][j] = MiniNero.addKeys(MiniNero.scalarmultKey(HP[i][j], s[i][j]), MiniNero.scalarmultKey(keyimage[i], c[j])) #Rj = sH + cxH
        tohash = tohash + L[i][j] + R[i][j]
      j = (j + 1) % cols
      c[j] = MiniNero.cn_fast_hash(tohash)
    for i in range(0, rows):
      s[i][index] = MiniNero.sc_mulsub_keys(s[i][index], c[index], xx[i]) #si = a - c x so a = s + c x
    return keyimage, c[0], s

def MLSAG_Ver(pk, keyimage, c1, s ):
    rows = len(pk)
    cols = len(pk[0])
    print("verifying MLSAG sig of dimensions ",rows ,"x ", cols)
    L = [[None]*cols]
    R = [[None]*cols]
    pj = ''.join(pk[0])
    for i in range(1, rows):
      L.append([None] * cols)
      R.append([None] * cols)
      pj = pj + ''.join(pk[i])
    c= [None]*(cols+1) #you do an extra one, and then check the wrap around 
    HP = [[MiniNero.hashToPoint_cn(i) for i in pk[0]]]
    for j in range(1, rows):
      HP.append([MiniNero.hashToPoint_cn(i) for i in pk[j]])
    c[0] = c1
    j = 0
    while j < cols:
      tohash = pj
      for i in range(0, rows):
        L[i][j] = MiniNero.addKeys(MiniNero.scalarmultBase(s[i][j]), MiniNero.scalarmultKey(pk[i][j], c[j]))
        R[i][j] = MiniNero.addKeys(MiniNero.scalarmultKey(HP[i][j], s[i][j]), MiniNero.scalarmultKey(keyimage[i], c[j]))
        tohash = tohash + L[i][j] + R[i][j]
      j = j + 1
      c[j] = MiniNero.cn_fast_hash(tohash)

    rv = (c[0] == c[cols])
    print("c", c)
    print("sig verifies?", rv)
    
    return rv
