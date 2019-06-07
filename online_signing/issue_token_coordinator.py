#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json
import boto3
import sys

#the reissuance token is hard coded to the federation block-signing script
reissuanceToken = "Xa4jPZTkSSe9SJ6BfEmE8NzNEPaPW849M8"

print("Issue a new asset")

print(" ")
print("Controller 1: Coordinator")
print(" ")

print("Load the mapping object - connecting to S3")
s3 = boto3.resource('s3')
s3.Bucket('cb-mapping').download_file('map.json','map.json')

map_obj = am.MapDB(2,3)
map_obj.load_json('map.json')
fmass = map_obj.get_total_mass()
print("    Total mass: "+str(fmass))
print("    Timestamp: "+str(map_obj.get_time())+" ("+datetime.fromtimestamp(map_obj.get_time()).strftime('%c')+")")
print("    Blockheight: "+str(map_obj.get_height()))
con_keys = am.ConPubKey()
con_keys.load_json('controllers.json')
key_list = con_keys.list_keys()
if map_obj.verify_multisig(key_list):
    print("    Signatures verified")
else:
    print("    Verification failed")
print(" ")

print("Load the P2SH address file")

with open('p2sh.json','r') as file:
    p2sh = json.load(file)

print(" ")

print("Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)
chaininfo = ocean.call('getblockchaininfo')
bestblockhash = chaininfo["bestblockhash"]
bestblock = ocean.call('getblock',bestblockhash)
print("    Current blockheight: "+str(chaininfo["blocks"]))
print("    Block time: "+str(bestblock["time"])+" ("+datetime.fromtimestamp(bestblock["time"]).strftime('%c')+")")
print(" ")

inpt = input("Enter number of asset issuances: ")
numiss = int(inpt)
print(" ")

assetRefList = []
assetYearList = []
assetManList = []
assetMassList = []
issueToAddressList = []

for issit in range(numiss):
	print("Asset issuance "+str(issit+1))

	inpt = input("    Enter issuance address: ")
	issueToAddress = str(inpt)
	issueToAddressList.append(issueToAddress)
	print(" ")
	print("    Specify asset reference data: ")
	print(" ")
	inpt = input("        Enter serial number: ")
	assetRef = str(inpt)
	inpt = input("        Enter year of manufacture: ")
	assetYear = str(inpt)
	inpt = input("        Enter manufacturer: ")
	assetMan = str(inpt)
	inpt = input("        Enter fine mass: ")
	assetMass = float(inpt)
	print(" ")
	assetRefList.append(assetRef)
	assetYearList.append(assetYear)
	assetManList.append(assetMan)
	assetMassList.append(assetMass)

print("Issuance of "+str(numiss)+" new assets")
print(" ")
print("  Serial number    Year      Manufacturer      Fine mass")
print("----------------------------------------------------------")
for issit in range(numiss):
	print("      "+assetRefList[issit]+"       "+assetYearList[issit]+"         "+assetManList[issit]+"           "+str(assetMassList[issit]))

print(" ")
inpt = input("Confirm data correct? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

chaininfo = ocean.call('getblockchaininfo')
print("Determine token issuance at block height "+str(chaininfo["blocks"]))
print(" ")
bheight = int(chaininfo["blocks"]) 
token_ratio = am.token_ratio(bheight)
print("    token ratio = "+str("%.13f" % token_ratio))

print(" ")
tokenAmountList = []
print("Token issuances: ")
for issit in range(numiss):
	tokenAmount = assetMassList[issit]/token_ratio
	assref = assetRefList[issit]+"-"+assetYearList[issit]+"-"+assetManList[issit]
	print("    Asset: "+assref+"  tokens = "+str("%.8f" % round(tokenAmount)))
	tokenAmountList.append(tokenAmount)

print(" ")

print("Create raw issuance transactions:")
#the UTXO database lists unspent policy asset outputs that can be used for issuance
#each line lists the txid, the vout, the value of the output and scriptPubKey

#get the current list from S3
s3.Bucket('cb-mapping').download_file('ptxo.dat','ptxo.dat')

with open("ptxo.dat") as file:
    utxolist = file.readlines()
utxolist = [x.strip() for x in utxolist]

if len(utxolist) < numiss:
	print("ERROR: more asset issuances than policy asset outputs")
	print("Exiting ...")
	sys.exit()

issuancetxList = []
txinList = []
for issit in range(numiss):
	txin = utxolist[issit].split()
	changeAmount = float(txin[2])
	issuancetx = ocean.call('createrawissuance',issueToAddressList[issit],str("%.8f" % tokenAmountList[issit]),reissuanceToken,'10000',p2sh["address"],str("%.8f" % changeAmount),'1',txin[0],str(int(txin[1])))
	print("    New token ID: "+issuancetx["asset"])
	issuancetxList.append(issuancetx)
	txinList.append(txin)

print(" ")
print("Add new entries to mapping object:")
print(" ")

for issit in range(numiss):
	addret = map_obj.add_asset(assetRefList[issit],assetYearList[issit],assetMassList[issit],issuancetxList[issit]["asset"],assetManList[issit])
	if addret == 0:
		print("ERROR: add asset error")
		print("Exiting ...")
		sys.exit()

tmass = map_obj.get_total_mass()
print("     New total mass: "+str(tmass))

print(" ")

print("Add partial signature to issuance transaction")

c1_privkey = open('c1_privkey.dat','r').read()
#version byte is 239 for ocean regtest mode
version_byte = 0
#encode private key to be importable to ocean client
c1_pk_wif = bc.encode_privkey(c1_privkey,'wif_compressed',version_byte)

partialSigTxList = {}
for issit in range(numiss):
	partial_sig_tx = ocean.call('signrawtransaction',issuancetxList[issit]["rawtx"],[{"txid":txinList[issit][0],"vout":int(txinList[issit][1]),"scriptPubKey":p2sh["scriptPubKey"],"redeemScript":p2sh["redeemScript"]}],[c1_pk_wif])
	partialSigTxList[issit] = partial_sig_tx

print("Add signature to mapping object:")
map_obj.clear_sigs()
map_obj.update_time()
map_obj.update_height(bheight)
map_obj.sign_db(c1_privkey,1)
print(" ")
print("Export partially signed data objects")
print(" ")
print("     ps1_map.json")
print("     ps1_tx.json")
map_obj.export_json("ps1_map.json")

#add the input transaction data to the tx file to enable the second signature to be generated
for issit in range(numiss):
	partialSigTxList[issit]["scriptPubKey"] = p2sh["scriptPubKey"]
	partialSigTxList[issit]["txid"] = txinList[issit][0]
	partialSigTxList[issit]["vout"] = txinList[issit][1]
	partialSigTxList[issit]["asset"] = issuancetxList[issit]["asset"]
	partialSigTxList[issit]["mass"] = assetMassList[issit]

partialSigTxList["numiss"] = numiss

with open("ps1_tx.json",'w') as file:
          json.dump(partialSigTxList,file)

#upload new partially signed objects 
s3.Object('cb-mapping','ps1_tx.json').put(Body=open('ps1_tx.json','rb'))
s3.Object('cb-mapping','ps1_map.json').put(Body=open('ps1_map.json','rb'))
