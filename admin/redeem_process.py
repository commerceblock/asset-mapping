#!/usr/bin/env python                                              
import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import time
import boto3
import sys
import json

testnet = False

#version byte is 111 for testnet, 0 for mainnet
if testnet:
    version_byte = 111
    addr_byte = 235
else:
    version_byte = 52
    addr_byte = 38

print("Redemption transaction processing")

privkey = open('frzlist_privkey.dat','r').read()
frzlistprivkey = bc.encode_privkey(privkey,'wif_compressed',version_byte)
frzpubkey_uc = bc.privkey_to_pubkey(privkey)
frzpubkey = bc.compress(frzpubkey_uc)
frzaddress = bc.pubkey_to_address(frzpubkey,addr_byte)

print("Load the mapping object - connecting to S3")
s3 = boto3.resource('s3')
s3.Bucket('cb-mapping').download_file('map.json','map.json')

map_obj = am.MapDB(2,3)
map_obj.load_json('map.json')

print("    Timestamp: "+str(map_obj.get_time())+" ("+datetime.fromtimestamp(map_obj.get_time()).strftime('%c')+")")
con_keys = am.ConPubKey()
con_keys.load_json('controllers.json')
key_list = con_keys.list_keys()
if map_obj.verify_multisig(key_list):
    print("    Signatures verified")
else:
    print("    Verification failed")
print(" ")

print("Load the redeem list object - rassets.json")
s3.Bucket('cb-mapping').download_file('rassets.json','rassets.json')
print(" ")

r_obj = {}
with open('rassets.json') as file:
    r_obj = json.load(file)

print("Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

chaininfo = ocean.call('getblockchaininfo')
blkh = int(chaininfo["blocks"])
token_ratio = am.token_ratio(blkh)
print("Token ratio = "+str("%.13f" % round(token_ratio,13))+" at block "+str(blkh))
print(" ")

reissue_count = 60 - int(chaininfo["blocks"]) % 60
print("This redemption transaction must be confirmed within the next "+str(reissue_count)+" blocks (minutes)")
inpt = input("Proceed? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()
print(" ")

rref = input("Enter redeemed asset reference: ")
print(" ")
rmass = map_obj.get_mass_assetid(rref)
if rmass < 0.1:
    print("Invalid asset reference")
    print("Exit")
    sys.exit()  

inlist = 0
locked = False
for asst in r_obj["assets"]:
    if asst["ref"] == rref:
        inlist = 1
        locked = asst["lock"]

if inlist == 0:
    print("Asset reference not in the redeemable asset list")
    print("Exit")
    sys.exit()

if locked:
    print("Entered asset already locked for redemption")
    print("Exit")
    sys.exit()     

print("Asset mass: "+str("%.9f" % rmass))
exptoken = am.token_amount(blkh,rmass)
print("Required tokens: "+str("%.8f" % round(exptoken,8)))
print(" ")

print("Read in redemption (freeze) transaction")
print(" ")

filenam = rref+".txn"
with open(filenam, 'r') as file:
    rtx = json.load(file)

rtxcheck = ocean.call('testmempoolaccept',rtx["hex"])

if rtxcheck["allowed"] == 0:
    print("Redemption transaction invalid")
    print(rtxcheck["reject-reason"])
    print("Exit")
    sys.exit()

print("    Redemption transaction valid")

rdecode = ocean.call('decoderawtransaction',rtx["hex"])

frztag = 0
tokentotal = 0.0
rAddresses = []
rAssets = []
for outs in rdecode["vout"]:
    if map_obj.get_mass_tokenid(outs["asset"]) < 0.1:
        print("ERROR: redemption transaction contains an un-mapped token")
        print("Exit")
        sys.exit()
    if outs["n"] == 0:
        if outs["scriptPubKey"]["addresses"][0] == "2dZRkPX3hrPtuBrmMkbGtxTxsuYYgAaFrXZ":
            frztag = 1
    else:
        if outs["scriptPubKey"]["type"] == "pubkeyhash":
            tokentotal += outs["value"]
            addrs = outs["scriptPubKey"]["addresses"][0]
            rAddresses.append(addrs)
            outasset = outs["asset"]
            rAssets.append(outasset)


if frztag == 0:
    print("Redemption transaction not freeze-tagged")
    print("Exit")
    sys.exit()

if int(round(tokentotal,8)*100000000) != int(round(exptoken,8)*100000000):
    print("Redemption transaction total tokens: "+str(tokentotal)+" is incorrect for current period")
    print("Exit")
    sys.exit()

print(" ")
print("    Redemption transaction has sufficient tokens")
print(" ")

print("ALL REDEMPTION CHECKS PASSED")

print("Locking asset in redeem list")

for i in range(len(r_obj["assets"])):
    if r_obj["assets"][i]["ref"] == rref:
        r_obj["assets"][i]["lock"] = True

with open('rassets.json','w') as file:
    json.dump(r_obj,file)

#upload new partially signed objects
s3.Object('cb-mapping','rassets.json').put(Body=open('rassets.json','rb'))

print("Add redemption transaction addresses to the freezelist")
print(" ")

#the client wallet we connect to via RPC is expected to have the private keys to the policy asset outputs

#the UTXO database lists unspent policy asset outputs that can be used for issuance
#check if policyasset address is already in wallet
inwallet = ocean.call('getaccount',frzaddress)
if not inwallet == "freezeasset":
    ocean.call('importprivkey',frzlistprivkey,"freezeasset",True)

paunspent = ocean.call('listunspent')

txinlst = []
for output in paunspent:
    if output["address"] == frzaddress:
        utxo = []
        utxo.append(output["txid"])
        utxo.append(output["vout"])
        utxo.append(output["amount"])
        frzlistasset = output["asset"]
        txinlst.append(utxo)

print(" ")
print("Policy asset UTXOs found: "+str(len(txinlst)))

sent_frz = []
#loop over output addresses
for itr in range(len(rAddresses)):
    txin = txinlst[itr]
    inpts = []
    inpt = {}
    inpt["txid"] = txin[0]
    inpt["vout"] = int(txin[1])
    inpts.append(inpt)
    otpts = []
    otpt = {}
    otpt["pubkey"] = frzpubkey
    otpt["value"] = txin[2]
    otpt["address"] = rAddresses[itr]
    otpts.append(otpt)
    freezetx = ocean.call('createrawpolicytx',inpts,otpts,0,frzlistasset)
    freezetx_signed = ocean.call('signrawtransaction',freezetx)
    freezetx_send = ocean.call('sendrawtransaction',freezetx_signed["hex"])
    sent_frz.append(freezetx_send)

print("Sent "+str(len(sent_frz))+" freezelist txs: ")
for snttx in sent_frz:
    print("    "+str(snttx))
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
    print("    Check policy transactins confirmed")
    confs = 0

    for issit in range(len(sent_frz)):
        gettx = ocean.call('getrawtransaction',sent_frz[issit],True)
        if "confirmations" in gettx: confs += 1
    if confs == len(sent_frz): unconfirmed = False

chaininfo = ocean.call('getblockchaininfo')
blkh2 = int(chaininfo["blocks"])
if blkh2 // 60 != blkh // 60:
    print("Inflation period expired: restart issuance process")
    print("Exit")
    sys.exit()
reissue_count = 60 - blkh2 % 60
if reissue_count < 3:
    print("Insufficient time for confirmation this period: new redemption amount required")
    print("Exit")
    sys.exit()

print("Submit redemption transaction to network")

rtxid = ocean.call('sendrawtransaction',rtx["hex"])

print(" ")
print("Redemption transaction TXID = "+str(rtxid))

unconfirmed = True
while unconfirmed:
    print("Pause for on-chain confirmation")
    for i in range(35):
        sys.stdout.write('\r')
        sys.stdout.write('.'*i)
        sys.stdout.flush()
        time.sleep(1)

    print(" ")
    print("    Check redemption transaction confirmed")
    confs = 0

    gettx = ocean.call('getrawtransaction',rtxid,True)
    if "confirmations" in gettx: unconfirmed = False

print("Redemption transaction confirmed and outputs frozen")
print("COMPLETE")
