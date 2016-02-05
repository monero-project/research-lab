#use at your own risk
#Note, this is not quite working apparently, 
#apparently the viewkeys from the main client and mymonero
#although, if they were derived consistently 
#(which seems reasonable) then it should work
import MiniNero
import mnemonic

def importMM(wordlist):
    print("for testing purposes only!")
    sk = MiniNero.recoverSK(wordlist)
    print("vk", vk)
    print("pvk", MiniNero.publicFromSecret(vk))
    key = mnemonic.mn_encode(sk)
    cks = MiniNero.electrumChecksum(key)
    print(key + " "+cks)

seed = raw_input("12 words?")
print(importMM(seed))
