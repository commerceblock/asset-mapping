#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json
import sys
import time

print("Connecting to Ocean client")
print(" ")
rpcport = 18885
rpcuser = 'user2'
rpcpassword = 'password2'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

#in this demonstration we have a single re-issuer and the private key is in the local node wallet
#ocean.call('importaddress',fedAddress)

#the main loop - this runs continuously

client = True

while client:
	

	blkhsh = ocean.call('generate',1)
	#get the current block
	bbhash = ocean.call('getbestblockhash')
	bestblock = ocean.call('getblockheader',bbhash)

	blockheight = int(bestblock["height"])

	print("Block: "+str(blockheight))

	time.sleep(60)

