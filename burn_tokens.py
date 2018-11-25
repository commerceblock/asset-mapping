#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json
import sys
import time

print("Burn tokens")
print(" ")
print("Connecting to Ocean client wallet")
print(" ")
rpcport = 18885
rpcuser = 'user2'
rpcpassword = 'password2'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

inpt = input("Freeze TxID: ")
txid = str(inpt)
print(" ")
inpt = input("Number of outputs: ")
print(" ")
nout = int(inpt)
vouts = []
for it in range(nout):
	inpt = input("  vout = ")
	vouts.append(int(inpt))
print(" ")

freezetx = ocean.call('getrawtransaction',txid,True)

amount_list = []
asset_list = []
for it in range(nout):
	for vout in freezetx["vout"]:
		if vout["n"] == vouts[it]:
			val = vout["value"]
			amount_list.append(val)
			asset_list.append(vout["asset"])

for it in range(nout):
	print("Burn "+str(amount_list[it])+" of asset "+asset_list[it])

print(" ")
inpt = input("Confirm Burn? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

for it in range(nout):
	
	burntx = ocean.call('createrawburn',txid,str(vouts[it]),asset_list[it],amount_list[it])
	signtx = ocean.call('signrawtransaction',burntx["hex"])
	sendtx = ocean.call('sendrawtransaction',signtx["hex"])

print("Burn transactions complete")
