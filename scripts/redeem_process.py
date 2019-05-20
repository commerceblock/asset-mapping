#!/usr/bin/env python                                              
import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import time
import boto3
import sys
import json

print("Redemption transaction backend process")

#address for the redemption fee and the required amount
fAddress = "2djv4Z8uMPrHTQDQb8SD23HQw5ZYV8FP4Vo"
rfee = 5.0

#freezelist asset locking address and public key
frzaddress = "2djv4Z8uMPrHTQDQb8SD23HQw5ZYV8FP4Vo"
frzpubkey = "02fcf2003147ba14b15c7bdacf85b8a714922a1023d96cf145536c4a326d9a7fb3"
frzlistprivkey = "KxbwNMSSpzmnRqc9MKMqpWwiEbNr12UPZydNPKu45LEssG6qpC2Y"

frzlistasset = "b689510578dd34a6d1625e9df34b8fc3a8b80437cf55ece6bc620fd65a64550c"

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
print("Token ratio = "+str("%.8f" % token_ratio)+" at block "+str(blkh))
print(" ")
imprtk = chaininfo = ocean.call('importprivkey',frzlistprivkey)

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

print("Asset mass: "+str("%.3f" % rmass))
exptoken = rmass/token_ratio
print("Required tokens: "+str("%.8f" % exptoken))
print(" ")

print("Read in redemption fee transaction")
print(" ")

with open('rfee.dat', 'r') as file:
    rfeetx = file.read()

feetxcheck = ocean.call('testmempoolaccept',rfeetx)

if feetxcheck["allowed"] == 0:
    print("Fee transaction invalid")
    print(feetxcheck["reject-reason"])
    print("Exit")
    sys.exit()

print("    Fee transaction valid")

feedecode = ocean.call('decoderawtransaction',rfeetx)

feetotal = 0.0
for outs in feedecode["vout"]:
    if outs["scriptPubKey"]["type"] == "pubkeyhash":
        if outs["scriptPubKey"]["addresses"][0] == fAddress:
            feetotal += outs["value"]

if feetotal < rfee:
    print("Fee transaction total tokens: "+str(feetotal)+" is insufficient")
    print("Exit")
    sys.exit()

print(" ")
print("    Fee transaction has sufficient tokens")
print(" ")

print("Read in redemption (freeze) transaction")
print(" ")

filenam = "rtx-"+rref+".dat"
with open(filenam, 'r') as file:
    rtx = file.read()

rtxcheck = ocean.call('testmempoolaccept',rtx)

if rtxcheck["allowed"] == 0:
    print("Redemption transaction invalid")
    print(rtxcheck["reject-reason"])
    print("Exit")
    sys.exit()

print("    Redemption transaction valid")

rdecode = ocean.call('decoderawtransaction',rtx)

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

if tokentotal < round(exptoken,6):
    print("Redemption transaction total tokens: "+str(feetotal)+" is insufficient")
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

#get the freezelist output list
with open("flo.dat",'r') as file:
    utxolist = file.readlines()
utxolist = [x.strip() for x in utxolist]

sent_frz = []
inplcy = []
invout = []
#loop over output addresses
for itr in range(len(rAddresses)):
    txin = utxolist[itr+7].split()
    inpts = []
    inpt = {}
    inpt["txid"] = txin[0]
    inplcy.append(txin[0])
    invout.append(txin[1])
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

#update policy output list
with open("flo.dat",'w') as file:
    for sline in utxolist:
        line = sline.split()
        for issit in range(len(sent_frz)):
            replaced = False
            if line[0] == inplcy[issit] and int(line[1]) == int(invout[issit]):
                file.write(sent_frz[issit]+" "+"0"+" "+str(line[2])+"\n")
                replaced = True
                break
        if not replaced:    
            file.write(line[0]+" "+str(line[1])+" "+str(line[2])+"\n")

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

print("Submit fee and redemption transactions to network")

ftxid = ocean.call('sendrawtransaction',rfeetx)
rtxid = ocean.call('sendrawtransaction',rtx)

##########################################################
# Notify custodian via email with ftxid and rtxid
##########################################################