import MiniNero
import ed25519
import binascii
import PaperWallet
import cherrypy
import os
import time
import bitmonerod
import SimpleXMR2


xmr_addr = "44TVPcCSHebEQp4LnapPkhb2pondb2Ed7GJJLc6TkKwtSyumUnQ6QzkCCkojZycH2MRfLcujCM7QR1gdnRULRraV4UpB5n4"
xmr_amount = "0.25"
xmr_pid = "d8dd8f42cb13f26dbbf86d2d1da061628cdd17781be95e58a21c845465a2c7f6"

bitmonerod.send(xmr_addr, float(xmr_amount), xmr_pid, 3) 

