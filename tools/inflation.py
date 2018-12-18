#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json
import sys
import time

print("Asset inflation protocol")
print(" ")

#the inflation schedule and parameters

#reissuance address: the address that inflated tokens are paid to
reissuanceAddr = "19mx1SCDKSo3UC5dnyTXAMsGfDpx1im9EJ"
#the reissuer address (for testing this is a node wallet adress) - will be the federation signing script
fedAddress = "1N2vis2xVUMpZYTxfHRbk4a8gFQFJ2ZiH9"
#annual inflation rate (not demurrage rate)
arate = 0.0101010101010101
#inflation interval (in blocks)
#60 blocks is 1 hour (at 1 block per minute)
interval = 5

print("Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

#in this demonstration we have a single re-issuer and the private key is in the local node wallet
#ocean.call('importaddress',fedAddress)

#the main loop - this runs continuously

client = True

while client:
	
	#load the current inflation register
	with open('inflation.json') as file:
		inreg = json.load(file)

	#re-issuance is performed every 60th block
	#is it re-issuance time?

	#get the current block
	bbhash = ocean.call('getbestblockhash')
	bestblock = ocean.call('getblockheader',bbhash)

	blockheight = int(bestblock["height"])
	prevheight = 0

	if blockheight%interval == 0 and prevheight != blockheight and False:

		#compare the last saved re-issuance with the current best block
		#TODO: handle the case where the blockchain stops
		if "height" in inreg:
			lastissuance = int(inreg["height"])
			blockdelta = blockheight-lastissuance
			ninterval = blockdelta // interval
			print("Blockdelta = "+str(blockdelta)+" nInterval = "+str(ninterval))
		else:
			inreg["height"] = blockheight
			ninterval = 1

		if ninterval > 1:
			print("WARNING: excess reissuance interval: "+str(blockdelta)+" blocks since last re-issuance")

		#retrieve the token report for re-issuing
		utxorep = ocean.call('getutxoassetinfo')

		#create asset registry to calculate totals
		asset_tot = {}

		#loop over every entry in the utxo asset report
		for entry in utxorep:
			asset = entry["asset"]

			amount_spendable = entry["amountspendable"]
			amount_frozen = entry["amountfrozen"]

			#skipping reissuance token outputs
			if amount_spendable+amount_frozen < 9.9:

				if asset in asset_tot:
					asset_tot[asset]["spend"] += amount_spendable
					asset_tot[asset]["frz"] += amount_frozen
				else:
					asset_tot[asset] = {}
					asset_tot[asset]["spend"] = amount_spendable
					asset_tot[asset]["frz"] = amount_frozen

		for ast,amnts in asset_tot.items():

			amount_reissue = 0.0
    		#get the total of previous frozen from the regester
			frztot = 0.0

			#find the token for this asset
			found_token = False
			for i,j in inreg.items():
				if i != "height":
					if j["asset"] == ast:
						rtoken = i
						found_token = True
						break
			if not found_token:
				print("ERROR: Token for asset "+ast+" not found")

			for frzn in inreg[rtoken]["frzlst"]:
				frztot += frzn["value"]
    		#if the frozen amount hasn't changed then just inflate the spendable
			elapsed_interval = 0
			amount_unfrozen = 0

			if frztot == amnts["frz"]:
				amount_reissue = amnts["spend"]
    		#if the frozen amount is now greater then add to the frozen list for this asset
			elif frztot < amnts["frz"]:
				amount_reissue = amnts["spend"]
				newfrz = {}
				newfrz["amount"] = amnts["frz"]-frztot
				newfrz["height"] = blockheight
				inreg[rtoken]["frzlst"].append(newfrz)
				#if the frozen amount has reduced then remove from the frozen list and backdate the reissuance
			else:
				amount_unfrozen = frztot-amnts["frz"]
				amount_reissue = amnts["spend"]
    			#find the entry
				el = -1
				for it in range(len(inreg[rtoken]["frzlst"])):
					if inreg[rtoken]["frzlst"][it]["amount"] == amount_unfrozen:
						el = it
						frzheight = inreg[rtoken]["frzlst"][it]["height"]
						elapsed_interval = blockheight-frzheight // 60
				#delete it from the asset frozen list
				del inreg[rtoken]["frzlst"][el]

			total_reissue = 0.0
    		#the spendable amount needs to be inflated over a period of 1 hour
			total_reissue += amount_reissue*(1.0+arate)**((1.0*ninterval)/(24*365))-amount_reissue
    		#the newly unfrozen amount needs to be inflated over a period between now and the frzdate
			total_reissue += amount_unfrozen*(1.0+arate)**(elapsed_interval/(24*365))-amount_unfrozen

			print("Reissue asset "+ast+" by "+str("%.8f" % total_reissue))

    		#create the reissuance transaction
			txid_in = inreg[rtoken]["txid"]
			vout_in = inreg[rtoken]["vout"]
			entropy = inreg[rtoken]["entropy"]
			reissuance_tx = ocean.call('createrawreissuance',reissuanceAddr,str("%.8f" % total_reissue),fedAddress,str(inreg[rtoken]["amount"]),txid_in,str(vout_in),entropy)
			signed_reissuance = ocean.call('signrawtransaction',reissuance_tx["hex"])
			submit = ocean.call('sendrawtransaction',signed_reissuance["hex"])

			inreg[rtoken]["txid"] = submit

		#update the timestamp
		inreg["height"] = blockheight

	else:
		#check wallet for watched addresses - add the UTXO info to the regester
		ritokenlist = ocean.call('listunspent')
		numtoks = 0
		#check if there is a new token paid to the reissuance address
		for unspent in ritokenlist:
			#check all addresses
			#re-issuance tokens have issued amount over 1000 as a convention
			if unspent["address"] == fedAddress and unspent["amount"] > 99.0:
				numtoks += 1
				#get the issuance entropy from the tx input
				reissuancetx = ocean.call('getrawtransaction',unspent["txid"],True)

				if reissuancetx["vin"][0]["issuance"]["isreissuance"]:
					token = unspent["asset"]
					inreg[token]["txid"] = unspent["txid"]
					inreg[token]["vout"] = unspent["vout"]
				else:
					#change entropy to assetEntropy with the new ocean
					token = reissuancetx["vin"][0]["issuance"]["token"]
					if not token in inreg:
						inreg[token] = {}
						inreg[token]["frzlst"] = []

					inreg[token]["entropy"] = reissuancetx["vin"][0]["issuance"]["entropy"]
					inreg[token]["asset"] = reissuancetx["vin"][0]["issuance"]["asset"]
					#if nothing in the register, add a new entry
					inreg[token]["txid"] = unspent["txid"]
					inreg[token]["vout"] = unspent["vout"]
					inreg[token]["amount"] = unspent["amount"]

		print("Found "+str(numtoks)+" reissuance token outputs out of "+str(len(ritokenlist)))
	#write registry to file
	with open('inflation.json','w') as file:
		json.dump(inreg,file)

	prevheight = blockheight

	#sleep for a minute - only check every minute
	time.sleep(15)

	newblock = ocean.call('getnewblockhex')
	time.sleep(1)
	blocksig = ocean.call('signblock',newblock)
	time.sleep(1)
	sigarr = []
	sigarr.append(blocksig)
	signedblock = ocean.call('combineblocksigs',newblock,sigarr)
	time.sleep(1)
	submitblock = ocean.call('submitblock',signedblock["hex"])
	print("New block: "+str(blockheight))
	time.sleep(12)

