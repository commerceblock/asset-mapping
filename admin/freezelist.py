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

print("Freezelist control wallet")
print(" ")

privkey = open('frzlist_privkey.dat','r').read()
frzlistprivkey = bc.encode_privkey(privkey,'wif_compressed',version_byte)
frzpubkey_uc = bc.privkey_to_pubkey(privkey)
frzpubkey = bc.compress(frzpubkey_uc)
frzaddress = bc.pubkey_to_address(frzpubkey,addr_byte)

print("Connecting to Ocean client")
print(" ")
rpcport = 8332
rpcuser = 'ocean'
rpcpassword = 'oceanpass'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

inpto = input("Add address to freezelist or remove from freezelist? (A/R)")

if inpto == 'A':

    inpt = input("Enter address: ")
    addresstofreeze = str(inpt)
    #the client wallet we connect to via RPC is expected to have the private keys to the policy asset outputs

    #the UTXO database lists unspent policy asset outputs that can be used for issuance
    #check if policyasset address is already in wallet
    inwallet = ocean.call('getaccount',frzaddress)
    if not inwallet == "freezeasset":
        print("Importing privkey ...")
        ocean.call('importprivkey',frzlistprivkey,"freezeasset",True)

    paunspent = ocean.call('listunspent')

    frzlistasset = paunspent[0]["asset"]

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

elif inpto == 'R':

    inpt = input("Enter address: ")
    addresstofreeze = str(inpt)
    #the client wallet we connect to via RPC is expected to have the private keys to the policy asset outputs

    #the UTXO database lists unspent policy asset outputs that can be used for issuance
    #check if policyasset address is already in wallet
    inwallet = ocean.call('getaccount',frzaddress)
    if not inwallet == "freezeasset":
        ocean.call('importprivkey',frzlistprivkey,"freezeasset",True)

    paunspent = ocean.call('listunspent')

    frzlistasset = paunspent[0]["asset"]

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

else:
    print("Invalid option")
