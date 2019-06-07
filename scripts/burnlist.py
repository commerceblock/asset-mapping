#!/usr/bin/env python                                              
import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import time
import boto3
import sys
import json

print("burnlist control wallet")
print(" ")

#burnlist asset locking address and public key
brnaddress = "2dscqGd9G5TkbARL2pKB2P9miTNLqEsCcYR"
brnpubkey = "03d507845c9469d242751bd93be62e6fc6e24284e77ea4182d5879b2403ddd77b0"
brnlistprivkey = "cSCMZ6nc5AgLpf2PamDon3xDznTfJNHKZTKei34AA9w5nh1Zte5a"

brnlistasset = "2d3c8502cb7e3450c46b3128490bb5999466cea2323b4aca0c9c65348df4555d"

print("Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

print("Add address to burnlist:")

inpt = input("Enter address: ")
addresstoburn = str(inpt)
#the client wallet we connect to via RPC is expected to have the private keys to the policy asset outputs

#the UTXO database lists unspent policy asset outputs that can be used for issuance
#check if policyasset address is already in wallet
inwallet = ocean.call('getaccount',brnaddress)
if not inwallet == "burnasset":
    ocean.call('importprivkey',brnlistprivkey,"burnasset",True)

paunspent = ocean.call('listunspent')

txinlst = []
for output in paunspent:
    if output["address"] == brnaddress:
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
otpt["pubkey"] = brnpubkey
otpt["value"] = txin[2]
otpt["address"] = addresstoburn
otpts.append(otpt)
burntx = ocean.call('createrawpolicytx',inpts,otpts,0,brnlistasset)
burntx_signed = ocean.call('signrawtransaction',burntx)
burntx_send = ocean.call('sendrawtransaction',burntx_signed["hex"])

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
    gettx = ocean.call('getrawtransaction',burntx_send,True)
    if "confirmations" in gettx: unconfirmed = False

print("Check burnlist for address: "+str(addresstoburn))
print(" ")

islisted = ocean.call('queryburnlist',addresstoburn)

if islisted:
    print("   Confirmed")
else:
    print("   Failed")


