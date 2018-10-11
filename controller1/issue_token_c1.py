#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json
import boto3
import sys

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
print("    Timestamp: "+str(map_obj.get_time())+" ("+datetime.fromtimestamp(map_obj.get_time()).strftime('%c'))
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

inpt = input("Enter issuance address:")
issueToAddress = str(inpt)
print(" ")
#the reissuance token is hard coded to the federation block-signing script
reissuanceToken = "1NfyrgYvmThxW83y4yD9cTPzB8XzY3fQj2"
print(" ")
print("    Issuance address: "+issueToAddress)
print("    Reissuance address: "+reissuanceToken)
print(" ")
print("Specify asset reference data: ")
print(" ")
inpt = input("        Enter serial number:")
assetRef = str(inpt)
inpt = input("        Enter year of manufacture:")
assetYear = str(inpt)
inpt = input("        Enter manufacturer:")
assetMan = str(inpt)
inpt = input("        Enter fine mass:")
assetMass = float(inpt)
print(" ")
print("        Ref: "+assetRef)
print("        Year: "+assetYear)
print("        Man: "+assetMan)
print("        Mass: "+str(assetMass))
print(" ")
inpt = input("Confirm data correct?")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

print("Determine token issuance on "+str(datetime.now()))
print(" ")
token_ratio,hour = am.token_ratio()
tokenAmount = assetMass/token_ratio
print("    hour = "+str(hour))
print("    tokens = "+str(tokenAmount))
print(" ")

print("Create raw issuance transaction:")
print(" ")
print("Select policy asset UTXO")
#the UTXO database lists unspent policy asset outputs that can be used for issuance
#each line lists the txid, the vout, the value of the output and scriptPubKey

#get the current list from S3
s3.Bucket('cb-mapping').download_file('ptxo.dat','ptxo.dat')

with open("ptxo.dat") as file:
    utxolist = file.readlines()
utxolist = [x.strip() for x in utxolist]
txin = utxolist[0].split()
print(" ")
print("    TxID: "+txin[0]+" vout: "+txin[1])
print("    Ammount: "+txin[2])
print(" ")
changeAmount = float(txin[2])
issuancetx = ocean.call('createrawissuance',issueToAddress,str("%.8f" % tokenAmount),reissuanceToken,'1000',p2sh["address"],str("%.8f" % changeAmount),'1',txin[0],str(int(txin[1])))
print("    New token ID: "+issuancetx["asset"])
print(" ")

print("Add new entry to mapping object:")
print(" ")
map_obj.add_asset(assetRef,assetYear,assetMass,issuancetx["asset"],assetMan)
map_obj.update_time()
tmass = map_obj.get_total_mass()
print("     New total mass: "+str(tmass))

print(" ")

print("Add partial signature to issuance transaction")
c1_privkey = open('c1_privkey.dat','r').read()
#version byte is 239 for ocean regtest mode
version_byte = 239-128
#encode private key to be importable to ocean client
c1_pk_wif = bc.encode_privkey(c1_privkey,'wif_compressed',version_byte)

partial_sig_tx = ocean.call('signrawtransaction',issuancetx["rawtx"],[{"txid":txin[0],"vout":int(txin[1]),"scriptPubKey":p2sh["scriptPubKey"],"redeemScript":p2sh["redeemScript"]}],[c1_pk_wif])
print("Add signature to mapping object:")
map_obj.sign_db(c1_privkey,1)
print(" ")
print("Export partially signed data objects")
print(" ")
print("     ps1_map.json")
print("     ps1_tx.json")
map_obj.export_json("ps1_map.json")

#add the input transaction data to the tx file to enable the second signature to be generated
partial_sig_tx["scriptPubKey"] = p2sh["scriptPubKey"]
partial_sig_tx["txid"] = txin[0]
partial_sig_tx["vout"] = txin[1]
partial_sig_tx["asset"] = issuancetx["asset"]
with open("ps1_tx.json",'w') as file:
          json.dump(partial_sig_tx,file)
