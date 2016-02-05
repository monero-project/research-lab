#monero paper wallet test code, shen noether mrl
#use at your own risk
import Crypto.Random.random as rand
import MiniNero
import mnemonic
l = 2**252 + 27742317777372353535851937790883648493

def skGen():
    return MiniNero.intToHex( 8 * (rand.getrandbits(64 * 8)) % l)

def pkGen():
    #The point of this is in testing functions where you need some arbitrary public key to test against
    return MiniNero.scalarmultBase(MiniNero.intToHex( 8 * (rand.getrandbits(64 * 8)) % l))

def skpkGen():
    #The point of this is in testing functions where you need some arbitrary public key to test against
    sk = skGen()
    return sk, MiniNero.scalarmultBase(sk)



def keysBoth():
    print("This is for private testing purposes only, use at your own risk!")
    print("this function will generate an address that is compatible both with the main client and with MyMonero")
    print("shen noether- mrl")
    print(" ")
    while True:
        print('.'),
        sk = skGen()

        #s = "3c817618dcbfed122a64e592bb441d73300da9123686224a84e0eab1f075117e"; for testing

        vk = MiniNero.getViewMM(sk) #note this is the sc_reduced version..
        worked = 1
        #uncomment below lines to make viewkey a point..
        try:
            MiniNero.toPoint(vk)
        except:
            worked =0
            print("bad vk")

        if vk == MiniNero.sc_reduce_key(vk) and worked == 1: #already reduced
            break
    print("found key")
    print("secret spend key:", sk)
    print("secret view key:", vk)
    pk = MiniNero.publicFromSecret(sk)
    print("public spend key:", pk)
    pvk = MiniNero.publicFromSecret(vk)
    print("public view key:", pvk)
    addr =  MiniNero.getAddrMM(sk)
    print("receiving address", addr)
    wl = mnemonic.mn_encode(sk)
    cks = MiniNero.electrumChecksum(wl)
    print(cks)
    print("mnemonic:", wl + " " + cks)
    return sk, vk, pk, pvk, addr, wl, cks

if __name__ == "__main__":
    keysBoth()
