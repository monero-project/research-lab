# shen noether - mrl
# this python script computes
# a (Keccak) hash of your document
# and then turns it into a monero address
# for timestamping c.f. github.com/ShenNoether/btcProof
#

import MiniNero #for creating monero address
import sys #for getting command line arguments
import binascii #for converting binary data
import Keccak #for hash, we use this instead of sha256
import ed25519
import mnemonic

BLOCKSIZE = 2 **10
l = 2**252 + 27742317777372353535851937790883648493
def cnHashOfFile(filepath):
    #c.f. github.com/ShenNoether/btcProof sha256OfFile
    bin_data = open(filepath, 'rb').read()
    hex_data = binascii.hexlify(bin_data)
    print(hex_data)
    return MiniNero.cn_fast_hash(hex_data)

def moneroProofOfFile(fi):
    s = cnHashOfFile(fi)
    #s = MiniNero.sc_reduce_key(s) #if you are testing, insert
    #an s below this line

    sk = MiniNero.sc_reduce_key(s)
    print("secret spend key:", sk)
    vk = MiniNero.getView(sk)
    print("secret view key:", vk)
    pk = MiniNero.publicFromSecret(sk)
    print("public spend key:", pk)
    pvk = MiniNero.publicFromSecret(vk)
    print("public view key:", pvk)
    wl = mnemonic.mn_encode(s)
    cks = MiniNero.electrumChecksum(wl)
    print(cks)
    print("mnemonic:", wl + " " + cks)

    return MiniNero.encode_addr(MiniNero.netVersion(), pk, pvk)

if len(sys.argv) > 1:
    #print("address to send to :", moneroProofOfFile(sys.argv[1]))
    cnHashOfFile(sys.argv[1])
else:
    print("provide filename as argument")
    print("example: MoneroProof.py Keccak.txt")

