#Elliptic Curve Diffie Helman with ed25519
#ecdhgen and ecdhretrieve translated into MiniNero from implementation by TacoTime
import MiniNero
import PaperWallet
def ecdhGen(P):
  ephembytes, ephempub = PaperWallet.skpkGen() 
  sspub = MiniNero.scalarmultKey(P, ephembytes) #(receiver pub) * (sender ecdh sk)
  ss1 = MiniNero.cn_fast_hash(sspub)
  ss2 = MiniNero.cn_fast_hash(ss1)
  return ephembytes, ephempub, ss1, ss2
  
def ecdhRetrieve(x, pk):
  sspub = MiniNero.scalarmultKey(pk, x)
  ss1 = MiniNero.cn_fast_hash(sspub)
  ss2 = MiniNero.cn_fast_hash(ss1)
  return ss1, ss2

