#The following code is taken for the most part from 
#https://github.com/moneroexamples/python-json-rpc.git
#I've slightly modified it to fit the cherry py server better

import requests
import json
import os
import binascii        

def send(destination_address, amount, payment_id, mixin):
    # simple wallet is running on the localhost and port of 18082
    url = "http://localhost:18082/json_rpc"
    # standard json header
    headers = {'content-type': 'application/json'}
    # cryptonote amount format is different then
    # that normally used by people.
    # thus the float amount must be changed to
    # something that cryptonote understands
    int_amount = int(get_amount(amount))

    # just to make sure that amount->coversion->back
    # gives the same amount as in the initial number
    assert amount == float(get_money(str(int_amount))), "Amount conversion failed"
    

    # send specified xmr amount to the given destination_address
    recipents = [{"address": destination_address,
                  "amount": int_amount}]
                  
    # simplewallet' procedure/method to call
    rpc_input = {
        "method": "transfer",
        "params": {"destinations": recipents,
                   "mixin": mixin,
                   "payment_id" : payment_id}
    }

    # add standard rpc values
    rpc_input.update({"jsonrpc": "2.0", "id": "0"})

    # execute the rpc request
    response = requests.post(
         url,
         data=json.dumps(rpc_input),
         headers=headers)

    # print the payment_id
    print("#payment_id: ", payment_id)

    # pretty print json output
    print(json.dumps(response.json(), indent=4))


def get_amount(amount):
    """encode amount (float number) to the cryptonote format. Hope its correct.

    Based on C++ code:
    https://github.com/monero-project/bitmonero/blob/master/src/cryptonote_core/cryptonote_format_utils.cpp#L211
    """

    CRYPTONOTE_DISPLAY_DECIMAL_POINT = 12

    str_amount = str(amount)

    fraction_size = 0

    if '.' in str_amount:

        point_index = str_amount.index('.')

        fraction_size = len(str_amount) - point_index - 1

        while fraction_size < CRYPTONOTE_DISPLAY_DECIMAL_POINT and '0' == str_amount[-1]:
            print(44)
            str_amount = str_amount[:-1]
            fraction_size = fraction_size - 1

        if CRYPTONOTE_DISPLAY_DECIMAL_POINT < fraction_size:
            return False

        str_amount = str_amount[:point_index] + str_amount[point_index+1:]

    if not str_amount:
        return False

    if fraction_size < CRYPTONOTE_DISPLAY_DECIMAL_POINT:
        str_amount = str_amount + '0'*(CRYPTONOTE_DISPLAY_DECIMAL_POINT - fraction_size)

    return str_amount


def get_money(amount):
    """decode cryptonote amount format to user friendly format. Hope its correct.

    Based on C++ code:
    https://github.com/monero-project/bitmonero/blob/master/src/cryptonote_core/cryptonote_format_utils.cpp#L751
    """

    CRYPTONOTE_DISPLAY_DECIMAL_POINT = 12

    s = amount

    if len(s) < CRYPTONOTE_DISPLAY_DECIMAL_POINT + 1:
        # add some trailing zeros, if needed, to have constant width
        s = '0' * (CRYPTONOTE_DISPLAY_DECIMAL_POINT + 1 - len(s)) + s

    idx = len(s) - CRYPTONOTE_DISPLAY_DECIMAL_POINT

    s = s[0:idx] + "." + s[idx:]

    return s    
    
    
def balance():

    # simple wallet is running on the localhost and port of 18082
    url = "http://localhost:18082/json_rpc"

    # standard json header
    headers = {'content-type': 'application/json'}

    # simplewallet' procedure/method to call
    rpc_input = {
           "method": "getbalance"
    }

    # add standard rpc values
    rpc_input.update({"jsonrpc": "2.0", "id": "0"})

    # execute the rpc request
    response = requests.post(
        url,
        data=json.dumps(rpc_input),
        headers=headers)

    # amounts in cryptonote are encoded in a way which is convenient
    # for a computer, not a user. Thus, its better need to recode them
    # to something user friendly, before displaying them.
    #
    # For examples:
    # 4760000000000 is 4.76
    # 80000000000   is 0.08
    #
    # In example 3 "Basic example 3: get incoming transfers" it is
    # shown how to convert cryptonote values to user friendly format.

    # pretty print json output
    print(json.dumps(response.json(), indent=4))
    
def myAddress():
        # simple wallet is running on the localhost and port of 18082
        url = "http://localhost:18082/json_rpc"

        # standard json header
        headers = {'content-type': 'application/json'}
        
        """return the wallet's address"""

        rpc_input = {
            "method": "getaddress"
        }

        response = do_rpc(url, headers, rpc_input)

        return response.json()        
        
def do_rpc(url,headers, rpc_input):
    """does the rpc calls"""

    # add standard rpc values
    rpc_input.update({"jsonrpc": "2.0", "id": "0"})

    # execute the rpc requrest
    response = requests.post(
        url,
        data=json.dumps(rpc_input),
        headers=headers)

    return response        