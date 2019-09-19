#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json
import boto3
import sys
import os

#the reissuance token is hard coded to the federation block-signing script
reissuanceToken = "g3X4Jwf9WLuBqET7tr2bCkDX3A2FGBrUm8"

print("Issue a new asset")

print(" ")
print("Controller 1: Coordinator")
print(" ")

print("Load the mapping object - connecting to S3")
s3 = boto3.resource('s3')
s3.Bucket('gtsa-mapping').download_file('map.json','map.json')

map_obj = am.MapDB(2,3)
map_obj.load_json('map.json')
fmass = map_obj.get_total_mass()
print("    Total mass: "+str(round(fmass,3)))
print("    Timestamp: "+str(map_obj.get_time())+" ("+datetime.fromtimestamp(map_obj.get_time()).strftime('%c')+")")
print("    Blockheight: "+str(map_obj.get_height()))

print(" ")
inpt = input("Confirm mapping mass and timestamp corresponds to last known change? ")
print(" ")
if str(inpt) != "Yes":
    inpt = input ("Response not recognised. Please type 'Yes' to continue. ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()
print(" ")

con_keys = am.ConPubKey()
con_keys.load_json('controllers.json')
key_list = con_keys.list_keys()
if map_obj.verify_multisig(key_list):
    print("    Signatures verified")
else:
    if round(fmass,3) > 0.0:
        print("    Verification failed - invalid or missing signatures")
        print("Exit")
        sys.exit()
    else:
        print("    Mapping object empty")
print(" ")

print("Load the P2SH address file")

with open('p2sh.json','r') as file:
    p2sh = json.load(file)

print(" ")

print("Connecting to Ocean client")
print(" ")
rpcport = 8332
rpcuser = 'ocean'
rpcpassword = 'oceanpass'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)
chaininfo = ocean.call('getblockchaininfo')
bestblockhash = chaininfo["bestblockhash"]
bestblock = ocean.call('getblock',bestblockhash)
print("    Current blockheight: "+str(chaininfo["blocks"]))
print("    Block time: "+str(bestblock["time"])+" ("+datetime.fromtimestamp(bestblock["time"]).strftime('%c')+")")
print("    System time: "+str(datetime.now().timestamp())+" ("+datetime.now().strftime('%c')+")")
print(" ")

if datetime.now().timestamp() > float(bestblock["time"]) + 100.0:
    print("ERROR: best block time more than 1 minute in the past")
    print("Check syncronisation of system clock, then contact system admin")
    print("Exit")
    sys.exit()

reissue_count = 480 - int(chaininfo["blocks"]) % 480
print("This issuance must be completed within the next "+str(reissue_count)+" blocks ("+str(reissue_count // 60)+"h "+str(reissue_count % 60)+"m)")
inpt = input("Proceed? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()
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
print("    token ratio = "+str("%.13f" % round(token_ratio,8)))

print(" ")
tokenAmountList = []
print("Token issuances: ")
for issit in range(numiss):
	tokenAmount = am.token_amount(bheight,assetMassList[issit])
	assref = assetRefList[issit]+"-"+assetYearList[issit]+"-"+assetManList[issit]
	print("    Asset: "+assref+"  tokens = "+str("%.8f" % round(tokenAmount,8)))
	tokenAmountList.append(round(tokenAmount,8))

print(" ")

print("Create raw issuance transactions:")
#the UTXO database lists unspent policy asset outputs that can be used for issuance
#check if policyasset address is already in wallet
inwallet = ocean.call('getaccount',p2sh["address"])
if not inwallet == "policyasset":
	ocean.call('importaddress',p2sh["address"],"policyasset",True)

paunspent = ocean.call('listunspent')

txin = []
for output in paunspent:
	if output["address"] == p2sh["address"]:
		utxo = []
		utxo.append(output["txid"])
		utxo.append(output["vout"])
		utxo.append(output["amount"])
		txin.append(utxo)

print(" ")
print("Policy asset UTXOs found: "+str(len(txin)))

if len(txin) < numiss:
	print("ERROR: more asset issuances than policy asset outputs")
	print("Exiting ...")
	sys.exit()

issuancetxList = {}
txinList = []
for issit in range(numiss):
	changeAmount = float(txin[issit][2])
	issuancetx = ocean.call('createrawissuance',issueToAddressList[issit],str("%.8f" % round(tokenAmountList[issit],8)),reissuanceToken,'10000',p2sh["address"],str("%.8f" % changeAmount),'1',txin[issit][0],str(int(txin[issit][1])))
	print("    New token ID: "+issuancetx["asset"])
	issuancetxList[str(issit)] = issuancetx
	txinList.append(txin[issit])

print(" ")
print("Add new entries to mapping object:")
print(" ")

for issit in range(numiss):
	addret = map_obj.add_asset(assetRefList[issit],assetYearList[issit],assetMassList[issit],issuancetxList[str(issit)]["asset"],assetManList[issit])
	if addret == 0:
		print("ERROR: add asset error")
		print("Exiting ...")
		sys.exit()

tmass = map_obj.get_total_mass()
print("     New total mass: "+str(round(tmass,3)))

print(" ")

print("Add signatures (on airgapped signing device):")
map_obj.clear_sigs()
map_obj.update_time()
map_obj.update_height(bheight)
print(" ")
print("Export partially signed data objects (to directory "+os.getcwd()+")")
print(" ")
print("     /Volumes/DGLD-SIGN/map_us.json")
print("     /Volumes/DGLD-SIGN/tx_us.json")
map_obj.export_json("/Volumes/DGLD-SIGN/map_us.json")

#save for archive
map_obj.export_json("map_us_log.json",True)

#add the input transaction data to the tx file to enable the second signature to be generated
for issit in range(numiss):
	issuancetxList[str(issit)]["scriptPubKey"] = p2sh["scriptPubKey"]
	issuancetxList[str(issit)]["txid"] = txinList[issit][0]
	issuancetxList[str(issit)]["vout"] = txinList[issit][1]
	issuancetxList[str(issit)]["mass"] = assetMassList[issit]

issuancetxList["numiss"] = numiss

with open("/Volumes/DGLD-SIGN/tx_us.json",'w') as file:
    json.dump(issuancetxList,file)

try:
    os.remove('/Volumes/DGLD-SIGN/tx_ps.json')
except OSError:
    pass

try:
    os.remove('/Volumes/DGLD-SIGN/map_ps.json')
except OSError:
    pass

inpt = input("Confirm transactions and mapping signed? ")
if str(inpt) != "Yes":
    inpt = input ("Response not recognised. Please type 'Yes' to continue. ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()
print(" ")

nfound = 0
for count in range(4):
	try:
		#upload new partially signed objects 
		s3.Object('gtsa-mapping','/Volumes/DGLD-SIGN/tx_ps.json').put(Body=open('/Volumes/DGLD-SIGN/tx_ps.json','rb'))
		s3.Object('gtsa-mapping','/Volumes/DGLD-SIGN/map_ps.json').put(Body=open('/Volumes/DGLD-SIGN/map_ps.json','rb'))
	except:
		inpt = input("ERROR: files not found. Check they have been copied correctly? ")
		if str(inpt) != "Yes":
			inpt = input ("Response not recognised. Please type 'Yes' to continue. ")
		if str(inpt) != "Yes":
    			print("Exit")
    			sys.exit()
		nfound += 1

if nfound > 3:
	print("ERROR: files not found, exiting.")
	print("Exit")
	sys.exit()

chaininfo = ocean.call('getblockchaininfo')
bheight = 480 - int(chaininfo["blocks"]) % 480
print("Partially signed issuance transactions and object uploaded to cloud")
print("Contact confirmer to complete the issuance within the next "+str(bheight // 60)+" hours "+str(bheight % 60)+" minutes)")
