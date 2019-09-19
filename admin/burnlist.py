#!/usr/bin/env python                                              
import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import time
import boto3
import sys
import json

testnet = False

#version byte is 111 for testnet, 0 for mainnet
if testnet:
    version_byte = 111
    addr_byte = 235
else:
    version_byte = 52
    addr_byte = 38

print("burnlist control wallet")
print(" ")

privkey = open('brnlist_privkey.dat','r').read()
brnlistprivkey = bc.encode_privkey(privkey,'wif_compressed',version_byte)
brnpubkey_uc = bc.privkey_to_pubkey(privkey)
brnpubkey = bc.compress(brnpubkey_uc)
brnaddress = bc.pubkey_to_address(brnpubkey,addr_byte)

print("Connecting to Ocean client")
print(" ")
rpcport = 8332
rpcuser = 'ocean'
rpcpassword = 'oceanpass'
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
        brnlistasset = output["asset"]
        txinlst.append(utxo)

print(" ")
print("Burnlist asset UTXOs found: "+str(len(txinlst)))

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


