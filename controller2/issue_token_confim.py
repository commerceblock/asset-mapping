#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
import amap.rpchost as rpc
import json
import time
import boto3
import sys
from datetime import datetime

print("Issue an new asset")
print(" ")
print("Controller 2: Confirmer")
print(" ")

print("Fetch the current mapping object - connecting to S3")
s3 = boto3.resource('s3')
s3.Bucket('cb-mapping').download_file('map.json','map.json')

map_obj = am.MapDB(2,3)
map_obj.load_json('map.json')
fmass = map_obj.get_total_mass()
print("    Total mass: "+str("%.3f" % fmass))
print("    Timestamp: "+str(map_obj.get_time())+" ("+datetime.fromtimestamp(map_obj.get_time()).strftime('%c')+")")
print("    Blockheight: "+str(map_obj.get_height()))
con_keys = am.ConPubKey()
con_keys.load_json('controllers.json')
key_list = con_keys.list_keys()
if map_obj.verify_multisig(key_list):
    print("    Signatures verified")
else:
    print("    Signature verification failed")
print(" ")

print("Fetch the partially signed objects")
s3.Bucket('cb-mapping').download_file('ps1_map.json','ps1_map.json')
s3.Bucket('cb-mapping').download_file('ps1_tx.json','ps1_tx.json')
print(" ")

print("Load the updated mapping object")
print(" ")
new_map_obj = am.MapDB(2,3)
new_map_obj.load_json('ps1_map.json')
nmass = new_map_obj.get_total_mass()
print("    Mass difference: "+str("%.3f" % (nmass-fmass)))
print("    Timestamp: "+str(new_map_obj.get_time())+" ("+datetime.fromtimestamp(new_map_obj.get_time()).strftime('%c')+")")
print("    Blockheight: "+str(new_map_obj.get_height()))
print(" ")
print("Create comparison report")
print(" ")
am.diff_mapping(map_obj,new_map_obj)
print(" ")
print("Confirm:")
print("    New entry consistent")
print("    Amounts correct")
print("    Destination addresses correct")
print(" ")

inpt = input("Confirm diff data correct? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

print("Load the P2SH address")

with open('p2sh.json','r') as file:
    p2sh = json.load(file)
print(" ")

print("Load the partially signed transaction")
with open('ps1_tx.json','r') as file:
    partial_tx = json.load(file)
print(" ")
print("Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)
chaininfo = ocean.call('getblockchaininfo')
print("    Current blockheight: "+str(chaininfo["blocks"]))
print("    Block time: "+str(chaininfo["mediantime"])+" ("+datetime.fromtimestamp(chaininfo["mediantime"]).strftime('%c')+")")
print(" ")

inpt = input("Enter new asset mass: ")
assetMass = float(inpt)
print(" ")
print("Confirm token issuance amount:")
print(" ")
bheight = chaininfo["blocks"]
token_ratio = token_ratio(bheight)
tokenAmount = assetMass/token_ratio
print("    token ratio = "+str("%.8f" % token_ratio))
print("    tokens now = "+str("%.8f" % tokenAmount))
decode_tx = ocean.call('decoderawtransaction',partial_tx["hex"])
txTokenAmount = decode_tx["vin"][0]["issuance"]["assetamount"]
print("    transaction tokens = "+str(txTokenAmount))
print(" ")
inpt = input("Confirm token issuance correct? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

print(" ")
print("Confirm addresses:")
print("    Issuance address: "+decode_tx["vout"][0]["scriptPubKey"]["addresses"][0])
print("    Re-issuance address: "+decode_tx["vout"][1]["scriptPubKey"]["addresses"][0])
print(" ")
inpt = input("Addresses correct? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

#hard-coded address for the block-signing script
if decode_tx["vout"][1]["scriptPubKey"]["addresses"][0] != "1N2vis2xVUMpZYTxfHRbk4a8gFQFJ2ZiH9":
    print("WARNING: re-issuance address is not the block-signing script")
    inpt = input("Proceed? ")
    print(" ")
    if str(inpt) != "Yes":
        print("Exit")
        sys.exit()
print(" ")

print("Add partial signature to issuance transaction")
c2_privkey = open('c2_privkey.dat','r').read()
#version byte is 239 for ocean regtest mode
version_byte = 0
#encode private key to be importable to client
c2_pk_wif = bc.encode_privkey(c2_privkey,'wif_compressed',version_byte)
print(" ")
full_sig_tx = ocean.call('signrawtransaction',partial_tx["hex"],[{"txid":partial_tx["txid"],"vout":int(partial_tx["vout"]),"scriptPubKey":partial_tx["scriptPubKey"],"redeemScript":p2sh["redeemScript"]}],[c2_pk_wif])

if full_sig_tx["complete"]:
    print("    2-of-3 signature complete and valid")
else:
    print("    2-of-3 signature incomplete or invalid")
    print("Exit")
    sys.exit()

decode_full = ocean.call('decoderawtransaction',full_sig_tx["hex"])

print(" ")
print("Update policy asset output list")
#the UTXO database lists unspent policy asset outputs that can be used for issuance                                              
#each line lists the txid, the vout, the value of the output and scriptPubKey

#get the current list from S3
s3.Bucket('cb-mapping').download_file('ptxo.dat','ptxo.dat')

with open("ptxo.dat",'r') as file:
    utxolist = file.readlines()
utxolist = [x.strip() for x in utxolist]

with open("ptxo.dat",'w') as file:
    for sline in utxolist:
        line = sline.split()
        if line[0] == partial_tx["txid"] and int(line[1]) == int(partial_tx["vout"]):
            continue
        else:
            file.write(line[0]+" "+str(line[1])+" "+str(line[2])+"\n")
    file.write(decode_full["txid"]+" "+"2"+" "+str(decode_full["vout"][2]["value"])+"\n")

#upload new list to S3
s3.Object('cb-mapping','ptxo.dat').put(Body=open('ptxo.dat','rb'))

print(" ")
inpt = input("Confirm transaction send? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

submitok = False
while not submitok:
    #check it is not a reissuance block - if it is wait a minute
    bbhash = ocean.call('getbestblockhash')
    bestblock = ocean.call('getblockheader',bbhash)
    blockheight = int(bestblock["height"])
    if blockheight%60 == 0:
        time.sleep(60)
    else:
        submitok = True

print("Submit transaction to Ocean network")
submit_tx = ocean.call('sendrawtransaction',full_sig_tx["hex"])
print("        txid: "+str(submit_tx))
print(" ")

unconfirmed = True
while unconfirmed:
    print("Pause for on-chain confirmation")
    for i in range(35):
        sys.stdout.write('\r')
        sys.stdout.write('.'*i)
        sys.stdout.flush()
        sleep(2)

    print(" ")
    print("    Check asset created on-chain")
    #call the token info rpc
    utxorep = ocean.call('getutxoassetinfo')
    asset_conf = False
    for entry in utxorep:
        if entry["asset"] == decode_tx["vin"][0]["issuance"]["asset"]:
            if entry["amountspendable"] == txTokenAmount:
                asset_conf = True
                unconfirmed = False
    if not asset_conf:
        print("WARNING: Issuance transaction not confirmed")
        sys.exit()
print(" ")
print("Asset on-chain issuance confirmed")
print(" ")
print("Add signature to mapping object:")
new_map_obj.sign_db(c2_privkey,2)
print(" ")
print("Check signatures")
if new_map_obj.verify_multisig(key_list):
    print("    Signatures verified")
else:
    print("    Signature verification failed")
    print("    ERROR: exit")
    sys.exit()
print(" ")

print("Export fully signed mapping object")
new_map_obj.export_json("map.json")
#upload new map to S3
s3.Object('cb-mapping','map.json').put(Body=open('map.json','rb'),ACL='public-read')