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
fAddress = "145GdSFkUusAr4K48W5JpPRnx1cn8C2iJE"
rfee = 0.002

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
exptoken = mass/token_ratio
print("Required tokens: "+str("%.8f" % exptoken))
print(" ")

print("Read in redemption fee transaction")
print(" ")

with open('rfee.dat', 'r') as file:
    rfeetx = file.read()

feetxcheck = ocean.call('testmempoolaccept',rfeetx)

if feetxcheck["accept"] == 0:
    print("Fee transaction invalid")
    print(feetxcheck["reject-reason"])
    print("Exit")
    sys.exit()

print("    Fee transaction valid")

feedecode = ocean.call('decoderawtransaction',rfeetx)

feetotal = 0.0
for outs in feedecode["vout"]:
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

if rtxcheck["accept"] == 0:
    print("Redemption transaction invalid")
    print(rtxcheck["reject-reason"])
    print("Exit")
    sys.exit()

print("    Fee transaction valid")

rdecode = ocean.call('decoderawtransaction',rfeetx)

frztag = 0
tokentotal = 0.0
rAddresses = []
for outs in rdecode["vout"]:
    if outs["n"] == 0:
        if outs["scriptPubKey"]["addresses"][0] == "1111111111111111111114oLvT2":
            frztag = 1
    else:
        tokentotal += outs["value"]
        addrs = outs["scriptPubKey"]["addresses"][0]
        rAddresses.append(addrs)

if frztag == 0:
    print("Redemption transaction not freeze-tagged")
    print("Exit")
    sys.exit()

if tokentotal < exptoken:
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
    json.dump(result,file)

#upload new partially signed objects
s3.Object('cb-mapping','rassets.json').put(Body=open('rassets.json','rb'))

print("Add redemption transaction addresses to the freezelist")
print(" ")

###########################################################################################
# Freezlist wallet transaction with the redemption transaction output addresses (rAddresses) as metadata
###########################################################################################

print("Pause for on-chain confirmation")
for i in range(35):
    sys.stdout.write('\r')
    sys.stdout.write('.'*i)
    sys.stdout.flush()
    time.sleep(1)

print("Submit fee and redemption transactions to network")

ftxid = ocean.call('sendrawtransaction',rfeetx)
rtxid = ocean.call('sendrawtransaction'rtx)

##########################################################
# Notify custodian via email with ftxid and rtxid
##########################################################