#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
import amap.rpchost as rpc
import json
import time
import boto3
import sys
import os
from datetime import datetime

#hard-coded federation blocksigning multisig address
reissuanceToken = "Xa4jPZTkSSe9SJ6BfEmE8NzNEPaPW849M8"

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
s3.Bucket('cb-mapping').download_file('map_ps.json','map_ps.json')
s3.Bucket('cb-mapping').download_file('tx_ps.json','tx_ps.json')
print(" ")

print("Load the updated mapping object")
print(" ")
new_map_obj = am.MapDB(2,3)
new_map_obj.load_json('map_ps.json')
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
with open('tx_ps.json','r') as file:
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
bestblockhash = chaininfo["bestblockhash"]
bestblock = ocean.call('getblock',bestblockhash)
print("    Current blockheight: "+str(chaininfo["blocks"]))
print("    Block time: "+str(bestblock["time"])+" ("+datetime.fromtimestamp(bestblock["time"]).strftime('%c')+")")

print(" ")
print("Confirm token issuances:")
print(" ")
bheight = chaininfo["blocks"]
token_ratio = am.token_ratio(bheight)
print("    token ratio = "+str("%.8f" % token_ratio))
print(" ")

numiss = int(partial_tx["numiss"])
for issit in range(numiss):
    tokenAmount = float(partial_tx[str(issit)]["mass"])/token_ratio
    decode_tx = ocean.call('decoderawtransaction',partial_tx[str(issit)]["hex"])
    txTokenAmount = decode_tx["vin"][0]["issuance"]["assetamount"]
    print("    mass = "+str("%.3f" % partial_tx[str(issit)]["mass"])+"   expected tokens = "+str("%.8f" % tokenAmount)+"   transaction tokens = "+str("%.8f" % txTokenAmount))

print(" ")
inpt = input("Confirm token issuance correct? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

print(" ")
print("Confirm addresses:")
print(" ")

for issit in range(numiss):
    decode_tx = ocean.call('decoderawtransaction',partial_tx[str(issit)]["hex"])
    print("    Issuance address: "+decode_tx["vout"][0]["scriptPubKey"]["addresses"][0]+"    Re-issuance address: "+decode_tx["vout"][1]["scriptPubKey"]["addresses"][0])

print(" ")
inpt = input("Addresses correct? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

#hard-coded address for the block-signing script
for issit in range(numiss):
    decode_tx = ocean.call('decoderawtransaction',partial_tx[str(issit)]["hex"])
    if decode_tx["vout"][1]["scriptPubKey"]["addresses"][0] != reissuanceToken:
        print("WARNING: re-issuance address is not the block-signing script")
        inpt = input("Proceed? ")
        print(" ")
        if str(inpt) != "Yes":
            print("Exit")
            sys.exit()
print(" ")

print("Add confirmer signature (on airgapped signing device) to exported files map_ps.json and tx_ps.json")
print(" ")
cwd = os.getcwd()
inpt = input("Confirm transactions and mapping signed (and copied to "+cwd+" directory as map_fs.json and tx_fs.json)? ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()
print(" ")

print("Load the fully signed transaction")
with open('tx_fs.json','r') as file:
    signed_tx = json.load(file)

print("Load the fully signed mapping")
with open('map_fs.json','r') as file:
    signed_map = json.load(file)

for issit in range(numiss):
    full_sig_tx = signed_tx[issit]
    if full_sig_tx["complete"]:
        print("    2-of-3 transaction signatures complete")
    else:
        print("    2-of-3 transaction signatures incomplete or invalid")
        print("Exit")
        sys.exit()

chaininfo = ocean.call('getblockchaininfo')
blkh = int(chaininfo["blocks"])
objbh = new_map_obj.get_height()
if blkh // 60 != objbh // 60:
    print("Inflation period expired: restart issuance process")
    print("Exit")
    sys.exit()   
reissue_count = 60 - blkh % 60
if reissue_count < 3:
    print("Insufficient time for confirmation: restart issuance process")
    print("Exit")
    sys.exit()
print("Issuance must be completed within the next "+str(reissue_count)+" blocks (minutes)")
print(" ")
inpt = input("Proceed? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()
print(" ")

print(" ")
inpt = input("Confirm send transactions? ")
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
        print("pause for next block")
        print(" ")
        time.sleep(60)
    else:
        submitok = True

print("Submit transactions to Ocean network")
print(" ")

for issit in range(numiss):
    submit_tx = ocean.call('sendrawtransaction',signed_tx[issit]["hex"])
    print("        txid: "+str(submit_tx))
    print(" ")

unconfirmed = True
while unconfirmed:
    print("Pause for on-chain confirmation")
    for i in range(35):
        sys.stdout.write('\r')
        sys.stdout.write('.'*i)
        sys.stdout.flush()
        time.sleep(1)

    print(" ")
    print("    Check assets created on-chain")
    #call the token info rpc
    utxorep = ocean.call('getutxoassetinfo')
    asset_conf = False
    confs = 0

    for issit in range(numiss):
        decode_full = ocean.call('decoderawtransaction',signed_tx[issit]["hex"])
        for entry in utxorep:
            if entry["asset"] == decode_full["vin"][0]["issuance"]["asset"]:
                if entry["amountspendable"] == decode_full["vin"][0]["issuance"]["assetamount"]:
                    asset_conf = True
                    confs += 1
    if confs == numiss: unconfirmed = False

signed_map_obj = am.MapDB(2,3)
signed_map_obj.load_json('map_fs.json')
print(" ")
print("Asset on-chain issuance confirmed")
print(" ")
print("Check mapping signatures: ")
if signed_map_obj.verify_multisig(key_list):
    print("    Signatures verified")
else:
    print("    Signature verification failed")
    print("    ERROR: exit")
    sys.exit()
print(" ")

print("Export fully signed mapping object")
signed_map_obj.export_json("map.json")
#upload new map to S3
s3.Object('cb-mapping','map.json').put(Body=open('map.json','rb'),ACL='public-read')
print(" ")
print("Issuance complete and verified")