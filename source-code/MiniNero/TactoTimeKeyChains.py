#you += hash(pubkey || index) to both the private scalar and public point
#<tacotime> [02:35:38] so to get priv_i and pub_i
#<tacotime> [02:36:06] priv_i = (priv + hash) mod N
#<tacotime> [02:37:17] pub_i = (pub + scalarbasemult(hash))
import MiniNero
import PaperWallet

sk, vk, pk, pvk, addr, wl, cks = PaperWallet.keysBoth()

print("making keychain")
for i in range(1, 600):
    index = MiniNero.intToHex(i)
    has = MiniNero.cn_fast_hash(pk + index)
    sk1 = MiniNero.sc_add_keys(sk, has)
    pk1 = MiniNero.addKeys(pk, MiniNero.scalarmultBase(has))
    pk1_check =  MiniNero.publicFromSecret(sk1)
    print("Check", pk1== pk1_check)
    print(sk1)
    #print("i, sk, pk", i, sk1, pk1)
