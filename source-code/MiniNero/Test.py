#!/usr/bin/python
import sys #for arguments
import MiniNero
import mnemonic
import PaperWallet
import Ecdh
import ASNL
import MLSAG
import MLSAG2
import LLW_Sigs
import RingCT
import Crypto.Random.random as rand
import Translator
import binascii


b = 256
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493


if len(sys.argv) >= 2:
    if sys.argv[1] == "id":
        Translator.hexToC(MiniNero.identity())

    if sys.argv[1] == "smult":
        a= "87a61352d86f5cb0e9d227542b6b4870b9a327d082d15ea64e0494b9a896c1ac"
        aG = MiniNero.scalarmultBase(a)
        print(aG)
        print(MiniNero.scalarmultKey(aG, a))
    if sys.argv[1] == "add":
        #once it's good
        A = PaperWallet.pkGen()
        A = "75819750158570adc58ad6f932c3704661d6cd8eafd3a14818293a17790fbf71"
        B = PaperWallet.pkGen()
        B = "5fbc56c82c6e40596c673e301b63e100f08b97723ead425ed38f2b55c7a6454f"
        AB = MiniNero.addKeys(A, B)
        Translator.hexToC(A)
        Translator.hexToC(B)
        print(AB)
        AAB = MiniNero.addKeys(AB, A)
        print("AAB", AAB)
        print("hash")
        print(MiniNero.sc_reduce_key(MiniNero.cn_fast_hash(A)))
        aAbB = MiniNero.addKeys(MiniNero.scalarmultKey(A, A), MiniNero.scalarmultKey(B, B))
        print("testing addKeys3")
        print(aAbB)

    if sys.argv[1] == "rs":
        #once it's good
        sk = MiniNero.randomScalar()
    if sys.argv[1] == "mn":
        #checking decoding mnemonic
        #seed = "code elope foiled knapsack abyss fishing wayside also joining auburn robot sonic inquest obnoxious pact gave smash itches fierce darted owed queen pool fruit auburn"
        seed = "down hairy tattoo ointment austere lush fossil symptoms vary sonic ultimate onslaught pioneer aerial kept linen unnoticed ahead weavers injury buzzer inquest justice nightly symptoms"
        seed = "unzip festival cease fences value anchor waking tomorrow ritual hookup guarded antics cease"
        sk = MiniNero.recoverSK(seed)
        print("sk", sk)
        print("addr my monero", MiniNero.getAddr(sk))
    if sys.argv[1] == "vk":
        #check making viewkey
        sk = "86c5616d91c7e7d96ec8220b15a5d441526ecc09f76347a40ab3a67373f8ba03"
        sk = "7eb3f0d43fbe9caee69215fbc360f49ce545d0dfae71390d531c9723cb25e904"
        vk = MiniNero.getView(sk)
        vk = "bb36fe9e852f617093a1634626268b61c5e5e065f503cbdd105877a0a54c3a02"
        print(vk)
    if sys.argv[1] == "addr":
        sk = "b6aafbbb9a6ee768bf292f7ebf977b6a31f51d4ecbf59186dd8367a3012f640f"
        sk = "7eb3f0d43fbe9caee69215fbc360f49ce545d0dfae71390d531c9723cb25e904"
        sk = "7c404922198b99c08020468c896f13df4f6e2ff1b5ab3c528e014cc9836ce80b"
        pk = MiniNero.publicFromSecret(sk)
        print("pk", pk)
        vk = "9e71628d6db09405a1267550b902299ed5cd004653e52d0a12129a21ab69900d"
        vk = "bb36fe9e852f617093a1634626268b61c5e5e065f503cbdd105877a0a54c3a02"
        vk = "7c404922198b99c08020468c896f13df4f6e2ff1b5ab3c528e014cc9836ce80b"
        vk = "c1c9e45989cc5fbfe828400886c50b4f58da40692d0f6ce6b3d483c4f1bf4b05"
        pvk = MiniNero.publicFromSecret(vk)
        print("pvk", pvk)
        vers = "12"
        print(MiniNero.encode_addr(vers, pk, pvk))
    if sys.argv[1] == "sp":
        a = "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
        a = "c8d603858291b23c42695fec0b3db1b7fcb961e63d885a89c6ef70507a0b3204"
        a = "7c404922198b99c08020468c896f13df4f6e2ff1b5ab3c528e014cc9836ce80b"
        b = MiniNero.publicFromSecret(a)
        print(b)
    if sys.argv[1] == "crc":
        #test vectors
        t = "salads wipeout algebra knife awakened jewels uneven tender nearby worry ferry macro uneven"
        t = "sadness uneven boil mammal highway zinger enmity inkling coal essential teeming vibrate drunk drowning sulking unnoticed muffin swagger quick musical aquarium equip gather linen quick"
        t = "tyrant bailed lynx symptoms winter pirate yanks jagged dawn germs daily left hull pedantic puppy dilute dash adventure pigment nodes hockey yodel across richly adventure"
        t = "irony leopard emotion bovine veteran spout weird soccer adventure jeopardy negative rabbits otter boyfriend jackets boil richly apricot cake hydrogen luggage menu muffin sushi menu"
        t = "ivory koala decay whole segments cement natural pact omega asylum onslaught pinched jive thumbs nouns pimple baffles uptight okay itself unmask ruthless asked fossil pact"
        t = "oneself zodiac aimless october comb egotistic vastness otherwise nobody shelter amidst nexus costume dash rotate evenings zones hope aimless jury onslaught copy excess unzip october"
        t = "fifteen eels reorder sneeze fidget inbound onboard tufts lifestyle rounded lilac opened ascend fonts recipe copy android launching unquoted doctor lids reinvest syllabus five sneeze"
        t = "vinegar bubble bobsled southern godfather toolbox online hoax error pegs dice pamphlet knapsack erase lottery aside myth surfer exotic wipeout idled pelican cell tiger aside"
        t = "aquarium safety null huddle vastness ruined taken hamburger rhythm costume lion cupcake pouch auburn hashing vulture vitals pigment dangerous possible each salads segments fazed vulture"
        t = "aquarium safety null huddle vastness ruined taken hamburger rhythm costume lion cupcake pouch auburn hashing vulture vitals pigment dangerous possible each salads segments fazed vulture"

        t = raw_input("13 or 25 words?")
        a = MiniNero.electrumChecksum(t)
        print(a)
    if sys.argv[1] == "1224":
        #sohuld turn 12 word key to 24
        print("tbd")
        sk = "536313cc0a88457e3d3e5aadda8d204af20e480416cc522ebd5a67df00ce2503"
        print(MiniNero.getAddr(sk))
    if sys.argv[1] == "seed":
        seed = "3c817618dcbfed122a64e592bb441d73300da9123686224a84e0eab1f075117e";
        a = MiniNero.hexToInt(seed)
        b = a // l
        print(b)
    if sys.argv[1] == "HCT":
        for i in [1, 12, 123, 1234, 12345, 123456]:
            A = MiniNero.publicFromInt(i)
            print(i, MiniNero.hashToPoint_ct(A))
    if sys.argv[1] == "RingCTSimple":
        #see below for ring ct with sliding exponents
        exponent = 9
        H_ct = RingCT.getHForCT()
        print("H", H_ct)
        sr, Pr = PaperWallet.skpkGen() #receivers private/ public
        se, pe, ss1, ss2 = Ecdh.ecdhGen(Pr) #compute shared secret ss
        digits = 32 #in practice it could will be 32 (from .0001 monero to ~400k monero) all other amounts can be represented by full 64 if necessary, otherwise you can use the sliding implementation of RingCT given below.
        print("inputs")
        a = 10000
        Cia, L1a, s2a, sa, ska = RingCT.genRangeProof(10000, digits)
        print("outputs")
        b = 7000
        Cib, L1b, s2b, sb, skb = RingCT.genRangeProof(7000, digits)
        c = 3000
        Cic, L1c, s2c, sc, skc = RingCT.genRangeProof(3000, digits)
        print("verifying range proofs of outputs")
        RingCT.verRangeProof(Cib, L1b, s2b, sb)
        RingCT.verRangeProof(Cic, L1c, s2c, sc)
        x, P1 = PaperWallet.skpkGen()
        P2 = PaperWallet.pkGen()
        C2 = PaperWallet.pkGen() #some random commitment grabbed from the blockchain
        ind = 0
        Ca = RingCT.sumCi(Cia)
        Cb = RingCT.sumCi(Cib)
        Cc = RingCT.sumCi(Cic)
        sk = [x, MiniNero.sc_sub_keys(ska, MiniNero.sc_add_keys(skb, skc))]
        pk = [[P1, P2], [MiniNero.subKeys(Ca, MiniNero.addKeys(Cb, Cc)), MiniNero.subKeys(C2, MiniNero.addKeys(Cb, Cc)) ] ]
        II, cc, ssVal = MLSAG.MLSAG_Sign(pk, sk, ind)
        print("Sig verified?", MLSAG.MLSAG_Ver(pk, II, cc, ssVal) )
        print("Finding received amount corresponding to Cib")
        RingCT.ComputeReceivedAmount(pe, sr, MiniNero.addScalars(ss1, skb),MiniNero.addScalars(ss2, MiniNero.intToHex(b)), Cib, 9)
        print("Finding received amount corresponding to Cic")
        RingCT.ComputeReceivedAmount(pe, sr, MiniNero.addScalars(ss1, skc), MiniNero.addScalars(ss2, MiniNero.intToHex(c)), Cic, 9)
    if sys.argv[1] == "MLSAG":
        #below is example usage. Uncomment each line for testing
        N = 3 #cols
        R = 3 #rows
        x = [[None]*N] #just used to generate test public keys
        sk = [None] * R #vector of secret keys
        P = [[None]*N] #stores the public keys

        ind = 2
        for j in range(0, R):
            if j > 0:
                x.append([None]*N)
                P.append([None]*N)
            for i in range(0, N):
                x[j][i] = PaperWallet.skGen()
                P[j][i] = MiniNero.scalarmultBase(x[j][i])
            sk[j] = x[j][ind]
        print("x", x)
        II, cc, ss = MLSAG.MLSAG_Sign(P, sk, ind) 
        print("Sig verified?", MLSAG.MLSAG_Ver(P, II, cc, ss) )
    if sys.argv[1] == "MLSAG2":
        #below is example usage. Uncomment each line for testing
        rows = 3 #cols
        cols = 3 #rows
        ind = 1

        x = MLSAG2.skmGen(rows, cols)
        sk = x[ind]
        P = MLSAG2.keyMatrix(rows, cols)
        for i in range(0, cols):
            P[i] = MLSAG2.vScalarMultBase(x[i])

        II, cc, ss = MLSAG2.MLSAG_Gen(P, sk, ind) 
        print("I", II)
        print("c0", cc)
        print("s", ss)
        print("Sig verified?", MLSAG2.MLSAG_Ver(P, II, cc, ss) )
    if sys.argv[1]== "MLSAGc":
        P = [["4a199991d80915f99870b702fb6b3fa7b127853c4ed12ac2bb071534b9b5dee6","86e2c2ec0262c465749fdb1940de954d87d1e6b96beda093bc185f329e157c53","e9e83e74299bd3cdad4c87c6548dba859680000740660d1f783486d4cafef79f"],["78656dbba0fdfd14fc99b4da8b73c81314b9e65eeaa4eac510ca4dd28bae63a0","987f7b1b498e6ec25ad2ce304300388396a374721a24602b16905eeeb9a42fb0","b1a9c583747a8815fa7a80452efb4f93042dc64db08b3d2f7ac5016ea2b882eb"],["d3ef77673ee441b2ca3b1f9e7f628df9f6306d89d8c5155c3c6ee4c9f5f51408","5423f77332aa6a015ddc70a82e27fe52c68ab47e08b5c07d03641194de4ea1fb","ec564efa1511f73f91649d942fff0921763e4be37ee114036bd584f7a8fb9fd9"]]
        cc = "cd12f7147c6c01dee58be3338244b6f386806020e2d266a6aac68a4ab4bfb28b"
        II = ["352d19bc0ab8b45241dc23c27c4598791d4e23cd370198aea8eee8c7b5eb7b1d","8e2bca011d5b1fadde79dee44329545ca903b7bd299c4719e7593ad096e96141","5c6fad47d9ec734dab1139c40d4f11482e3d1f76585643520697a17f687a5962"]
        ss = [["e26f3115a50a2a25f1ec9582a4f4058f7f5c1b3f467cc38b0e882df7f93d6d0a","6b20f43b1f3c56ff3070b1a9a4612c808c35787a26243f5c046e283ff1b68f09","5091182154ad97d33c8210954b0570ccf95e8bedc5c6c193bde7d562bd9dc20a"],["ac297d01a6923e1c79d0fff82ecbfe0ae6ce515ef2b0dbc7e6b2f6542b99a404","c5371c10d7e7071ce3b3016db65bb29194e91a09cf428237fcf4037de74b5d03","a357b1453acd01fa101593994f60014f8ee7657921690bb4dfb0cfc41ef20802"],["a4a6ceb8454754ad32c987bcc56a03432155b47315f8805a3577a0470b0b330d","0ec6b71c2c6ba34d34bc3ea27e6813091fb3a90dc261a77fc9f46068bb1a3b09","41417b047353352e145fd3e65fe1e51e95081a64e9fda561060167e132c5e602"]]

        rows = 3 #cols
        cols = c #rows
        print("I", II)
        print("c0", cc)
        print("s", ss)
        print("Sig verified?", MLSAG2.MLSAG_Ver(P, II, cc, ss) )


 
    if sys.argv[1] == "LLW":
        #below is example usage
        N = 3
        x = [None]*N
        P = [None]*N
        HP = [None]*N
        for i in range(0, N):
            x[i] = PaperWallet.skGen()
            P[i] = MiniNero.scalarmultBase(x[i])
        print("x", x)
        pjoin = ''.join(P)
        ind = 0
        II, cc, ss = LLW_Sigs.LLW_Sig(P[:], x[ind], ind )
        print("Sig verified?", LLW_Sigs.LLW_Ver(P[:], II, cc, ss[:]) )
    if sys.argv[1] == "Ecdh":
        x1, pk1 = PaperWallet.skpkGen() #receiver secret key / public key
        ephem, ephempub, ss = Ecdh.ecdhGen(pk1) #ephempub is public key to create shared key
        ss2 = Ecdh.ecdhRetrieve(x1, ephempub)
        print "shared secret from sender: "
        print ss
        print "shared secret calculated by receiver: "
        print ss2
    if sys.argv[1] == "Schnorr":
        #test basic schnorr
        mes = "a very long test message asdflgkjnasdbfblkjnsdfblkjnsdfbklmnsdfbkl;jnsdfblkjsndfgblkjnserfvliksjndcmblkjxncvblikjhnwersfiodusjbsndlfigb7uvy3qo890eruiyghsblfduihjbo 9sruifjtyghbnqliownfghjbdlfkjvnb"
        sec = "7c404922198b99c08020468c896f13df4f6e2ff1b5ab3c528e014cc9836ce80b"
        pub = MiniNero.scalarmultBase(sec)
        r, c = ASNL.GenSchnorr(mes, sec, pub)
        print("sig verifies?",ASNL.VerSchnorr(mes, pub, r, c))
        print("sig verifies?",ASNL.VerSchnorr(mes, pub, r, PaperWallet.skGen()))
    if sys.argv[1] == "SchnorrNL":
        #test schnorr nonlinkable
        x, P2 = PaperWallet.skpkGen()
        P1 = PaperWallet.pkGen()
        L1, s1, s2 = ASNL.GenSchnorrNonLinkable(x, P1, P2, 1)
        ASNL.VerSchnorrNonLinkable(P1, P2, L1, s1, s2)
    if sys.argv[1] == "ASNL":
        #below tests ASNL code
        N = 10
        x = [None] * N
        P1 = [None] * N
        P2 = [None] * N
        indi = [None] * N
        for j in range(0, N):
            indi[j] = rand.getrandbits(1)
            x[j] = PaperWallet.skGen()
            if indi[j] == 0:
               P1[j] = MiniNero.scalarmultBase(x[j])
               P2[j] = PaperWallet.pkGen()
            else:
               P2[j] = MiniNero.scalarmultBase(x[j])
               P1[j] = PaperWallet.pkGen()
        L1, s2, s = ASNL.GenASNL(x, P1, P2, indi)
        ASNL.VerASNL(P1, P2, L1, s2, s)
    if sys.argv[1] == "brief":
        #shows compatibility with Ref10 (c.f. with sh runtest.sh in brief directory
        sec = "77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a"
        P = MiniNero.scalarmultBase(sec)
        print(P)
    if sys.argv[1] == "RingCT":
        #global stuff, i.e. inputs
        exponent = 9
        H_ct = RingCT.getHForCT()
        sr, Pr = PaperWallet.skpkGen() #receivers private/ public
        digits = 14 #in practice you can either specify it as part of the  protocol, or allow a sliding value
        a = 10
        b = 7
        c = 3
        P2 = PaperWallet.pkGen()
        C2 = PaperWallet.pkGen() #some random commitment grabbed from the blockchain
        x, P1 = PaperWallet.skpkGen()
        ind = 0

        #From the previous transaction
        print("inputs")
        Ca, Cia, L1a, s2a, sa, ska = RingCT.genRangeProof(a, digits)

        #Actions performed by sender
        se, pe, ss1, ss2 = Ecdh.ecdhGen(Pr) #compute shared secret ss
        print("outputs")
        Cb, Cib, L1b, s2b, sb, skb = RingCT.genRangeProof(b, digits)
        Cc, Cic, L1c, s2c, sc, skc = RingCT.genRangeProof(c, digits)
        print("verifying range proofs of outputs")
        RingCT.verRangeProof(Cib, L1b, s2b, sb) #only need these for outputs (the input above is assumed in a previous transaction..
        RingCT.verRangeProof(Cic, L1c, s2c, sc)
        pk, II, cc, ssVal = RingCT.genRCTSig([x], [ska], [skb, skc], [P1, P2], [[Ca], [C2]], [Cb, Cc], [[exponent],[3]], [exponent, exponent], 0)

        #Actions performed by the Miner
        print("Sig verified?", MLSAG.MLSAG_Ver(pk, II, cc, ssVal) )

        #Actions performed by receiver(s)
        print("Finding received amount corresponding to Cib")
        RingCT.ComputeReceivedAmount(pe, sr, MiniNero.addScalars(ss1, skb),MiniNero.addScalars(ss2, MiniNero.intToHex(b)), Cib, 9)
        print("Finding received amount corresponding to Cic")
        RingCT.ComputeReceivedAmount(pe, sr, MiniNero.addScalars(ss1, skc), MiniNero.addScalars(ss2, MiniNero.intToHex(c)), Cic, 9)
    if sys.argv[1] == "ctest":
        sk, Pk= PaperWallet.skpkGen()  
        print("running scalarmult base on ", sk, Pk)
        Translator.t_header()
        Translator.hexToC(sk, "sec")
        Translator.t_scalarmultBase("sec", "pub")
        Translator.t_footer()
    if sys.argv[1] == "chash":
        #pk = "ff33f4df1f8f44bfed3572134814f83c890495bd4714a0aaff0e0239c1acc927"
        sk, Pk= PaperWallet.skpkGen()  
        #h = MiniNero.cn_fast_hash(pk)
        #print("pk", pk)
        #Translator.hexToC(pk, "pub")
        #print("hash", h)
        Translator.t_header()
        Translator.hexToC(sk, "sec")
        Translator.t_scalarmultBase("sec", "pub")
        Translator.t_cn_fast_hash("pub", "h")
        Translator.t_footer()
    if sys.argv[1] == "cSchnorr":
        prefix = "a very long test message asdflgkjnasdbfblkjnsdfblkjnsdfbklmnsdfbkl;jnsdfblkjsndfgblkjnserfvliksjndcmblkjxncvblikjhnwersfiodusjbsndlfigb7uvy3qo890eruiyghsblfduihjbo 9sruifjtyghbnqliownfghjbdlfkjvnb"
        hash_prefix = MiniNero.cn_fast_hash(binascii.hexlify(prefix))

        h="247a9b60e8a31c18bfab9f6bf7b5079bc8c1955ea6726ea3f2bc38a3ec1bc658"
        pubb="ff33f4df1f8f44bfed3572134814f83c890495bd4714a0aaff0e0239c1acc927"
        sec="9d5f81503e5280cd8fdcd12c94bea81bdf4c2f87ebc0992ab177fba51db92c0a" 
        r, c = ASNL.GenSchnorr(h,pubb, sec, PaperWallet.skGen())
        Translator.sigToC(r, c)
        print("verd?", ASNL.VerSchnorr(h, pubb, r, c))
    if sys.argv[1] == "data":
        skv = ["ae5934fe1e8065ec19afc80f2f06fc3f36730405a022813e2b18dc9da929da02", "2a9f99b0313157ba599bde727e04d6bfe87163f1d7dc93a352b1a648d7178205", "f0fb4504b06785caac17f4c554526685eed71d21b9b542f50c6e396b6152a403", "e5f7c934aa59c2ea21efeb4695d09bb95402d0dcc92d5bbec59eb1fc5912cf0f", "795f05824fb9e4a0808a523ecc9fefcb9e563e152d9b101224cb18169d3a4a05"]
        pkv = MLSAG2.vScalarMultBase(skv)
        print(pkv)
    if sys.argv[1] == "addKeys":
      a, A = ('13e467e9c0034e6878af5c801a81ee0543b1096b5ab01356b349cc3235cd1909', 'a50e5e751a9906f9ff086c734591d0ee87be6ca58fe7208b8e070e54d2eda0da')
      b, B = ('cd43ec6b80dd5ea2668e141fc6dc1191258b5eb58bf7dbef9e647aca3ba09707', '4f31e64eb9017ac02c6313294d0554d4532fbd6ffd15bc175422060867ab33f4')
      Translator.hexToC(a)
      Translator.hexToC(b)
      print(MiniNero.addKeys1(a, b, B))
      print(MiniNero.addKeys2(a, A, b, B))
    if sys.argv[1] == "bighash":
      from bighash import *
      print(MiniNero.cn_fast_hash(a))
      b = "d99e55005f1736e5d843dd11ce80e3e989f3eea52a42e14f6c541620568569ed"
    if sys.argv[1] == "ch":
        a = "18a5f3cf50ae2207d8ccd70179a13b4fc339d0cd6d9138c6d764f8e4cef8f006c87b1367fef3f02ed5ffd42a7ea212c2b8899af3af8f4b1e34139e1e390f3af1"
        print(MiniNero.cn_fast_hash(a))
    if sys.argv[1] == "fastbin":
        b = "0123456789abcdef"
        c = MiniNero.hexToInt(b)
        c = 6000
        print(b, c)
        Translator.hexToC(b)
        b = RingCT.binary(c, 64)
        b2 = ''.join([str(a) for a in b])
        print(b2)
    if sys.argv[1] == "HPow2":
        A = MiniNero.publicFromInt(1)
        HPow2 = MiniNero.hashToPoint_ct(A)
        two = MiniNero.intToHex(2)
        for j in range(1, 64):
            key = HPow2
            while len(key) < 64:
                key = key + "0"
            k2 = [key[i:i+2] for i in range(0, len(key), 2)]
            ar = "{0x"+(", 0x".join(k2))+"}, "
            print(ar)
            HPow2 = MiniNero.scalarmultKey(HPow2, two)
        print("};")
    if sys.argv[1] == "h2":
        A = MiniNero.publicFromInt(1)
        H = MiniNero.hashToPoint_ct(A)
        print(MiniNero.addKeys(H, H))
        print(MiniNero.scalarmultKey(H, MiniNero.intToHex(2)))
          





