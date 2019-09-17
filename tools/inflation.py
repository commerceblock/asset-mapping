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
reissuanceAddr = "1Fbz57Pdez6MqwgwHP3PDcVXEFtPR3rfzr"
#the reissuer address (for testing this is a node wallet adress) - will be the federation signing script
fedAddress = "18j5iek2k1Aw7LDEZpopGuir9hpeM1q7yS"
#annual inflation rate (not demurrage rate)
arate = 0.0101010101010101
#inflation interval (in blocks)
#60 blocks is 1 hour (at 1 block per minute)
interval = 60

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
	
	#re-issuance is performed every 60th block
	#is it re-issuance time?

	#get the current block
	bbhash = ocean.call('getbestblockhash')
	bestblock = ocean.call('getblockheader',bbhash)

	blockheight = int(bestblock["height"])
	prevheight = 0

	if blockheight%interval == 0 and prevheight != blockheight:

		print("Inflation step")

		#retrieve the token report for re-issuing
		utxorep = ocean.call('getutxoassetinfo')

		unspentlist = ocean.call('listunspent')

		for unspent in unspentlist:
			#check all addresses
			#re-issuance and policy tokens have issued amount over 100 as a convention
			if "address" in unspent:
				if unspent["address"] == fedAddress and unspent["amount"] > 99.0:

					#find the reissuance details and amounts
					for entry in utxorep:
						if entry["token"] == unspent["asset"]:
							amount_spendable = entry["amountspendable"]
							amount_frozen = entry["amountfrozen"]
							asset = entry["asset"]
							entropy = entry["entropy"]
							print("as: "+str(amount_spendable)+" af: "+str(amount_frozen)+" as: "+asset+" en: "+entropy)
							break

					#the spendable amount needs to be inflated over a period of 1 hour
					total_reissue = amount_spendable*(1.0+arate)**(1.0/(24*365))-amount_spendable
					print("spend reissue: "+ str(total_reissue))

					#check to see if there are any assets unfrozen in the last interval
					amount_unfrozen = 0.0
					frzhist = ocean.call('getfreezehistory')
					for frzout in frzhist:
						if frzout["asset"] == asset:
							if frzout["end"] != 0 and frzout["end"] > blockheight - interval:
								backdate = blockheight - frzout["start"]
								elapsed_interval = backdate // interval
								print("elapsed_interval: "+str(elapsed_interval))
								amount_unfrozen = frzout["value"]
								total_reissue += amount_unfrozen*(1.0+arate)**(elapsed_interval/(24*365))-amount_unfrozen
								print("backdate reissue: "+ str(total_reissue))

					print("Reissue asset "+asset+" by "+str("%.8f" % total_reissue))

					if total_reissue == 0.0: continue

					reissuance_tx = ocean.call('createrawreissuance',reissuanceAddr,str("%.8f" % total_reissue),fedAddress,str(unspent["amount"]),unspent["txid"],str(unspent["vout"]),entropy)
					signed_reissuance = ocean.call('signrawtransaction',reissuance_tx["hex"])
					submit = ocean.call('sendrawtransaction',signed_reissuance["hex"])

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
	print("New block: "+str(blockheight+1))
	time.sleep(12)
