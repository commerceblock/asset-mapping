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
print("Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

inpt = input("Enter total mass: ")
assetMass = float(inpt)
print(" ")

print("Determine equivalent tokens on "+str(datetime.now()))
print(" ")
token_ratio,hour = am.token_ratio()
tokenAmount = assetMass/token_ratio
print("    hour = "+str(hour))
print("    token ratio = "+str("%.8f" % token_ratio))
print("    tokens = "+str("%.8f" % tokenAmount))
print(" ")
print("Determine token outputs")

tokenamnt = tokenAmount
amount_list = []
token_list = []
txid_list = []
vout_list = []
#find tokens to burn
unspentlist = ocean.call('listunspent')
for unspent in unspentlist:
	if unspent["amount"] < 9.9:
		if unspent["amount"] >= tokenamnt:
			amount_list.append(tokenamnt)
			token_list.append(unspent["asset"])
			txid_list.append(unspent["txid"])
			vout_list.append(unspent["vout"])
			change_amount = unspent["amount"] - tokenamnt
			change_asset = unspent["asset"]
			break
		else:
			amount_list.append(unspent["amount"])
			token_list.append(unspent["asset"])
			txid_list.append(unspent["txid"])
			vout_list.append(unspent["vout"])
			tokenamnt -= unspent["amount"]

#tokens sent to burn address
for it in range(len(amount_list)):
	print("Burn "+str("%.8f" % amount_list[it])+" of token "+token_list[it])

print(" ")
print("Change "+str("%.8f" % change_amount)+" of token "+change_asset)

print(" ")
print("Generate burn transactions")
inpt = input("Enter change address: ")
changeAddress = str(inpt)
print(" ")

for it in range(len(amount_list)-1):
	inputs = []
	outpoint = {}
	outpoint["txid"] = txid_list[it]
	outpoint["vout"] = vout_list[it]
	inputs.append(outpoint)

	burnout = {}
	burnout["data"] = "dead"

	print(inputs)
	print(burnout)

	burntx = ocean.call('createrawtransaction',inputs,burnout)
	subtx = ocean.call('sendrawtransaction',burntx)

inputs = []
outpoint = {}
outpoint["txid"] = txid_list[len(amount_list)]
outpoint["vout"] = vout_list[len(amount_list)]
inputs.append(outpoint)

burnout = {}
burnout["data"] = "dead"
burnout[changeAddress] = change_amount
burntx = ocean.call('createrawtransaction',inputs,burnout)
subtx = ocean.call('sendrawtransaction',burntx)
