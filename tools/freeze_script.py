#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json
import sys
import time

print("Create redemption transaction")
print(" ")
print("Connecting to Ocean client")
print(" ")
rpcport = 18885
rpcuser = 'user2'
rpcpassword = 'password2'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

inpt = input("Enter mass of redemption asset: ")
assetMass = float(inpt)
print(" ")

inpt = input("Enter full reference of redemption asset: ")
assetRef = inpt
print(" ")

chaininfo = ocean.call('getblockchaininfo')
bheight = int(chaininfo["blocks"])
bestblockhash = chaininfo["bestblockhash"]
bestblock = ocean.call('getblock',bestblockhash)
print("Current blockheight: "+str(bheight))
print("Blockchain time: "+str(bestblock["time"])+" ("+datetime.fromtimestamp(bestblock["time"]).strftime('%c')+")")
print(" ")

token_ratio = am.token_ratio(bheight)
tokenAmount = am.token_amount(bheight,assetMass)

print("    Token ratio = "+str("%.13f" % token_ratio))
print("    Tokens required = "+str("%.8f" % round(tokenAmount,8)))
print(" ")

changeAddress = ocean.call('getnewaddress')

print(" ")
print("Determine token inputs")

tokenamnt = tokenAmount
amount_list = []
token_list = []
txid_list = []
vout_list = []
suf = False
#find tokens to burn
unspentlist = ocean.call('listunspent')
for unspent in unspentlist:
	if unspent["amount"] < 9999.0:
		if unspent["amount"] >= tokenamnt:
			amount_list.append(tokenamnt)
			token_list.append(unspent["asset"])
			txid_list.append(unspent["txid"])
			vout_list.append(unspent["vout"])
			change_amount = unspent["amount"] - tokenamnt
			change_asset = unspent["asset"]
			suf = True
			break
		else:
			amount_list.append(unspent["amount"])
			token_list.append(unspent["asset"])
			txid_list.append(unspent["txid"])
			vout_list.append(unspent["vout"])
			tokenamnt -= unspent["amount"]

if not suf:
    print("ERROR: Insufficient tokens in wallet")
    sys.exit()

#tokens sent to burn address
for it in range(len(amount_list)):
	print("Freeze "+str("%.8f" % amount_list[it])+" of token "+token_list[it])

print(" ")
print("Change "+str("%.8f" % change_amount)+" of token "+change_asset)

print(" ")
print("Create funding transaction")
print(" ")
fee = 0.001
inputs = []
outputs = {}
assetpairs = {}
for it in range(len(amount_list)):
	tempAddress = ocean.call('getnewaddress')
	if it == len(amount_list)-1:
		outputs[tempAddress] = round(float(amount_list[it]),8)
	else:
		outputs[tempAddress] = round(float(amount_list[it]),8)
	assetpairs[tempAddress] = token_list[it]
	outpoint = {}
	outpoint["txid"] = txid_list[it]
	outpoint["vout"] = vout_list[it]
	inputs.append(outpoint)

outputs["fee"] = fee
outputs[changeAddress] = round(change_amount - fee,8)
assetpairs[changeAddress] = change_asset
assetpairs["fee"] = change_asset

fundingtx = ocean.call('createrawtransaction',inputs,outputs,0,assetpairs)
fundingtxsigned = ocean.call('signrawtransaction',fundingtx)
txsend = ocean.call('sendrawtransaction',fundingtxsigned["hex"])

print("Create freeze transaction")
print(" ")

inputs = []
outputs = {}
assetpairs = {}
#set zero address flag
outputs['1111111111111111111114oLvT2'] = fee
assetpairs['1111111111111111111114oLvT2'] = change_asset
for it in range(len(amount_list)):
	redemptionAddress = ocean.call('getnewaddress')
	print("    Redemption address: "+redemptionAddress)
	outputs[redemptionAddress] = round(float(amount_list[it]),8)
	assetpairs[redemptionAddress] = token_list[it]
	outpoint = {}
	outpoint["txid"] = txsend
	outpoint["vout"] = it
	inputs.append(outpoint)

print(" ")

freezetx = ocean.call('createrawtransaction',inputs,outputs,0,assetpairs)
freezetxsigned = ocean.call('signrawtransaction',freezetx)

print("Signed redemption transaction (hex encoded): ")
print(" ")
print(freezetxsigned["hex"])

print("Writing transaction to file: rtx-"+assetRef+".dat")
with open("rtx-"+assetRef+".dat",'w') as file:
	file.write(freezetxsigned["hex"])
