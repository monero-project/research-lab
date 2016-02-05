import MiniNero
import os
import ed25519
import binascii
import PaperWallet

import json, hmac, hashlib, time, requests

#gets xmr address, xmr amount, and pid for xmr2 order
#inputs are btc destination, and amount in btc
#also will return the order id, so you can track the order
def btc2xmr(dest, amount):
    #First create the order..
    url = 'https://xmr.to/api/v1/xmr2btc/order_create/'   
    payload = {'btc_dest_address' : dest, 'btc_amount' : amount}
    headers = {'content-type': 'application/json'}   
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    data = json.loads(r.content)
    uuid = data['uuid']
    print("uuid=", uuid)
    
    #wait a few seconds 
    print("waiting a few seconds for order to be created")
    for i in range(0, 5):
        print(".")
        time.sleep(1)    
        
    #get amount, address, pid
    ipStatus = 'https://xmr.to/api/v1/xmr2btc/order_status_query/'
    dat = {
        'uuid' : uuid
        }
    r2 = requests.post(ipStatus, data=json.dumps(dat), headers = headers) 
    #print(r2.text)
    data2 = json.loads(r2.content)
    xmr_amount = data2['xmr_required_amount']
    xmr_addr = data2['xmr_receiving_address']
    xmr_pid = data2['xmr_required_payment_id']
    print("send ", str(xmr_amount), " xmr to", xmr_addr, "with pid", xmr_pid)        
    return uuid, xmr_amount, xmr_addr, xmr_pid
    
    
    
#dest = "1em2WCg9QKxRxbo6S3xKF2K4UDvdu6hMc" #your dest address here
#amount = "0.1" #your amount here...

#uuid, xmr_amount, xmr_addr, xmr_pid = btc2xmr(dest, amount)
    
