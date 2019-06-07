#!/usr/bin/env python                                              
import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import time
import boto3
import sys
import json

print("Freezelist control wallet")
print(" ")

#freezelist asset locking address and public key
frzaddress = "2djv4Z8uMPrHTQDQb8SD23HQw5ZYV8FP4Vo"
frzpubkey = "02fcf2003147ba14b15c7bdacf85b8a714922a1023d96cf145536c4a326d9a7fb3"
frzlistprivkey = "xxxxxxxxxxxxxxxxxx"

frzlistasset = "b689510578dd34a6d1625e9df34b8fc3a8b80437cf55ece6bc620fd65a64550c"

print("Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

print("Add address to freezelist:")

inpt = input("Enter address: ")
addresstofreeze = str(inpt)
#the client wallet we connect to via RPC is expected to have the private keys to the policy asset outputs

#the UTXO database lists unspent policy asset outputs that can be used for issuance
#check if policyasset address is already in wallet
inwallet = ocean.call('getaccount',frzaddress)
if not inwallet == "freezeasset":
    ocean.call('importprivkey',frzlistprivkey,"freezeasset",True)

paunspent = ocean.call('listunspent')

txinlst = []
for output in paunspent:
    if output["address"] == frzaddress:
        utxo = []
        utxo.append(output["txid"])
        utxo.append(output["vout"])
        utxo.append(output["amount"])
        txinlst.append(utxo)

print(" ")
print("Policy asset UTXOs found: "+str(len(txinlst)))

txin = txinlst[0]
inpts = []
inpt = {}
inpt["txid"] = txin[0]
inpt["vout"] = int(txin[1])
inpts.append(inpt)
otpts = []
otpt = {}
otpt["pubkey"] = frzpubkey
otpt["value"] = txin[2]
otpt["address"] = addresstofreeze
otpts.append(otpt)
freezetx = ocean.call('createrawpolicytx',inpts,otpts,0,frzlistasset)
freezetx_signed = ocean.call('signrawtransaction',freezetx)
freezetx_send = ocean.call('sendrawtransaction',freezetx_signed["hex"])

unconfirmed = True
while unconfirmed:
    print("Pause for on-chain confirmation")
    for i in range(35):
        sys.stdout.write('\r')
        sys.stdout.write('.'*i)
        sys.stdout.flush()
        time.sleep(1)

    print(" ")
    print("    Check policy transactins confirmed")
    gettx = ocean.call('getrawtransaction',freezetx_send,True)
    if "confirmations" in gettx: unconfirmed = False

print("Check freezelist for address: "+str(addresstofreeze))
print(" ")

islisted = ocean.call('queryfreezelist',addresstofreeze)

if islisted:
    print("   Confirmed")
else:
    print("   Failed")


