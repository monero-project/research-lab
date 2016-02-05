q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493
import MiniNero
import PaperWallet

a = 3655169758690262480859172686034352748701568204867449275194046101565641063400
b = 2196281112309589493539510630657048805544016132079821556435431458072258858680
c = 1680308020000391016811131033972168547846809685867129675902005632340344199616
d = 3102886190919558838979092227453570755967767872654511102581747930112259050736
e = a + b + c + d
print(e, e % l)
pk = MiniNero.publicFromSecret(MiniNero.intToHex(e))
pka = MiniNero.publicFromSecret(MiniNero.intToHex(a))
pkb = MiniNero.publicFromSecret(MiniNero.intToHex(b))
pkc = MiniNero.publicFromSecret(MiniNero.intToHex(c))
pkd = MiniNero.publicFromSecret(MiniNero.intToHex(d))
A = MiniNero.addKeys(pka, pkb)
B = MiniNero.addKeys(A, pkc)
C = MiniNero.addKeys(B, pkd)
print(C)
print(pk)

