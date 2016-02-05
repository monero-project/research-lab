import MiniNero
import ed25519
import binascii
import PaperWallet
import cherrypy
import os
import time
import bitmonerod
import SimpleXMR2
import SimpleServer

message = "send0d000114545737471em2WCg9QKxRxbo6S3xKF2K4UDvdu6hMc"
message = "send0d0114545747771em2WCg9QKxRxbo6S3xKF2K4UDvdu6hMc"
sec = raw_input("sec?")
print(SimpleServer.Signature(message, sec))

