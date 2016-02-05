#monero determinstic vk wallet test code, shen noether mrl
#use at your own risk
import Crypto.Random.random as rand
import MiniNero
import mnemonic

def deterministicVK():
    while True:
        print('.'),
        tmp = MiniNero.intToHex(rand.getrandbits(64 * 8)) # 8 bits to a byte ...  
        sk = MiniNero.sc_reduce_key(MiniNero.cn_fast_hash(tmp))


        #s = "3c817618dcbfed122a64e592bb441d73300da9123686224a84e0eab1f075117e"; for testing
        #sk = MiniNero.sc_reduce_key(s)
        vk = MiniNero.getViewMM(sk) #note this is the sc_reduced version..
        worked = 1
        try:
            MiniNero.toPoint(vk)
        except:
            worked =0
            print("bad vk")
        if vk == MiniNero.sc_reduce_key(vk) and worked == 1: #already reduced + vk on curve
            break

    print("found keys")
    print("secret spend key:", sk)
    print("secret view key:", vk)
    vk2 = MiniNero.cn_fast_hash(MiniNero.scalarmultKey(vk, 2))
    print("secret view key2:", vk2)
    vk3 = MiniNero.cn_fast_hash(MiniNero.scalarmultKey(vk, 3))
    print("secret view key3:", vk3)

    pk = MiniNero.publicFromSecret(sk)
    print("public spend key:", pk)
    pvk = MiniNero.publicFromSecret(vk)
    print("public view key:", pvk)
    pvk2 = MiniNero.publicFromSecret(vk2)
    print("public view key2:", pvk2)
    pvk3 = MiniNero.publicFromSecret(vk3)
    print("public view key3:", pvk3)

    addr =  MiniNero.getAddrMM(sk)
    print("in future this will get all addresses")
    print("receiving address", addr)
    wl = mnemonic.mn_encode(s)
    cks = MiniNero.electrumChecksum(wl)
    print(cks)
    print("mnemonic:", wl + " " + cks)

deterministicVK()

