import MiniNero
def getHForCT():
    A = MiniNero.publicFromInt(123456)
    return MiniNero.hashToPoint_ct(A)

H = getHForCT()
for i in range(0, 2**14):
    print(MiniNero.scalarmultKeyInt(H, i))

