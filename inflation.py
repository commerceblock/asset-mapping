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
reissuanceAddr = "2dnZWwMzoK8jc8yTDd1d4R7SHzfikbUQEEk"
#the reissuer address (for testing this is a node wallet adress) - will be the federation signing script
fedAddress = "2deTjBefrA9mo8B3xEGGr3bnYX3UuAETiWu"
#annual inflation rate (not demurrage rate)
arate = 0.0101010101010101
#inflation interval (in seconds)
interval = 60*60

print("Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

#in this demonstration we have a single re-issuer and the private key is in the loal node wallet

#the main loop - this runs continuously

client = True

while client:
	
	#load the current inflation register
	with open('inflation.json') as file:
		inreg = json.load(file)

	#re-issuance is performed on the hour, every hour
	#is it re-issuance time?
	tinit = datetime.now()
	minit = tinit.minute
	if minit == 0:

		#get the current block
		bbhash = = ocean.call('getbestblockhash')
		bestblock = ocean.call('getblockheader',bbhash)

		#compare the last saved re-issuance with the current best block
		lastissuance = datetime.strptime(inreg["datetime"], "%Y-%m-%d %H:%M:%S.%f")
		blocktime = datetime.fromtimestamp(bestblock["time"])
		#check that the blocktime is within 3 minute of the system time
		if (datetime.now()-blocktime).minute > 3:
			print("Warning: blockchain time anomoly - missing blocks or clock failure")

		timedelta = blocktime-lastissuance
		ninterval = timedelta // interval

		#retrieve the token report for re-issuing
		utxorep = ocean.call('getutxoassetinfo')

		#loop over how many hours have elapsed since the last re-issuance
		for nhours in range(ninterval):

			#loop over every entry in the utxo asset report
			for entry in utxorep:
			    asset = entry["asset"]

    			amount_spendable = entry["amountspendable"]
    			amount_frozen = entry["amountfrozen"]

    			amount_reissue = 0.0
    			#get the total of previous frozen from the regester
    			frztot = 0.0
    			for frzn in inreg[asset]["frzlst"]:
    				frztot += frzn["value"]
    			#if the frozen amount hasn't changed then just inflate the spendable
    			if frztot == amount_frozen:
    				amount_reissue = amount_spendable
    			#if the frozen amount is now greater then add to the frozen list for this asset
    			else if frztot < amount_frozen:
    				amount_reissue = amount_spendable
    				newfrz = {}
    				newfrz["amount"] = amount_frozen-frztot
    				newfrz["datetime"] = str(tinit)
    				inreg[asset]["frzlst"].append(newfrz)
    			#if the frozen amount has reduced then remove from the frozen list and backdate the reissuance
    			else:
    				#get the time
    				amount_unfrozen = frztot-amount_frozen
    				#find the entry
    				el = -1
    				for it in range(len(inreg[asset]["frzlst"])):
    					if inreg[asset]["frzlst"][it]["amount"] == amount_unfrozen:
    						el = it
    						strfrzdate = inreg[asset]["frzlst"][it]["datetime"]
    						frzdate = datetime.strptime(strfrzdate, "%Y-%m-%d %H:%M:%S.%f")
    				#delete it from the asset frozen list
    				del inreg[asset]["frzlst"][it]

    			total_reissue = 0.0
    			#the spendable amount needs to be inflated over a period of 1 hour
    			total_reissue += amount_reissue*(1.0+arate)**(1.0/(24*365))-amount_reissue
    			#the newly unfrozen amount needs to be inflated over a period between now and the frzdate
    			elapsed_hours = (tinit-frzdate).seconds // 3600
    			total_reissue += amount_unfrozen*(1.0+arate)**(elapsed_hours/(24*365))-amount_unfrozen

    			#create the reissuance transaction
    			txid_in = inreg[asset]["txid"]
    			vout_in = inreg[asset]["vout"]
    			entropy = inreg[asset]["entropy"]
    			reissuance_tx = ocean.call('createrawreissuance',reissuanceAddr,total_reissue,fedAddress,inreg[asset]["amount"],txid_in,str(vout_in),entropy)
    			signed_reissuance = ocean.call('signrawtransaction',reissuance_tx["hex"])
        		submit = ocean.call('sendrawtransaction',signed_reissuance["hex"])

        		inreg[asset]["txid"] = submit

	#update the timestamp
    inreg["datetime"] = tinit

	else:
		#check wallet for watched addresses - add the UTXO info to the regester
		ritokenlist = ocean.call('listunspent')

		#check if there is a new token paid to the reissuance address
		for unspent in ritokenlist:
			#check all addresses
			#re-issuance tokens have issued amount over 1000 as a convention
			if unspent["address"] == fedAddress and unspent["amount"] > 1000:
				if not unspent["asset"] in inreg:
					#if nothing in the register, add a new entry
					inreg[unspent["asset"]]["txid"] = unspent["txid"]
					inreg[unspent["asset"]]["vout"] = unspent["vout"]
					inreg[unspent["asset"]]["amount"] = unspent["amount"]
					#get the issuance entropy from the tx input
					reissuancetx = ocean.call('getrawtransaction',unspent["txid"],True)
					inreg[unspent["asset"]]["entropy"] = reissuancetx["vin"][0]["issuance"]["entropy"]

	#write registry to file
	with open('inflation.json','w') as file:
		json.dump(inreg,file)

	#sleep for a minute - only check every minute
	time.sleep(60)

