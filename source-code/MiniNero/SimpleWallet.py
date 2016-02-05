import os
sec = raw_input("wallet pass?")
os.system(" ~/bitmonero/build/release/bin/simplewallet --wallet-file ~/wallet/testwallet1 --password "+sec+" --rpc-bind-port 18082")
