#!/usr/bin/env python                                              
import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import time
import boto3
import sys
import json

print("Redemption of tokens for a specified asset")

print(" ")
print("Controller 1: Coordinator")
print(" ")

print("Load the mapping object - connecting to S3")
s3 = boto3.resource('s3')
s3.Bucket('cb-mapping').download_file('map.json','map.json')

map_obj = am.MapDB(2,3)
map_obj.load_json('map.json')
fmass = map_obj.get_total_mass()
print("    Total mass: "+str("%.3f" % fmass))
print("    Timestamp: "+str(map_obj.get_time())+" ("+datetime.fromtimestamp(map_obj.get_time()).strftime('%c')+")")
con_keys = am.ConPubKey()
con_keys.load_json('controllers.json')
key_list = con_keys.list_keys()
if map_obj.verify_multisig(key_list):
    print("    Signatures verified")
else:
    print("    Verification failed")
print(" ")

print("Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

print("Specify asset redemption data: ")
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
print("        Ref: "+assetRef)
print("        Year: "+assetYear)
print("        Man: "+assetMan)
print("        Mass: "+str("%.3f" % assetMass))
print(" ")
inpt = input("Confirm data correct? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

print(" ")
rref = assetRef+"-"+assetYear+"-"+assetMan
print("Redemption of asset: "+rref)
print(" ")

if assetMass != map_obj.get_mass_assetid(rref):
    print("ERROR: total mass of asset "+rref+" in object = "+str("%.3f" % map_obj.get_mass_assetid(rref)))
    print("Exit")
    sys.exit()

rdate = datetime.strptime(input('Enter the redemption date and hour in the format year-month-day:hour: '), "%Y-%m-%d:%H")
print(" ")
print("    Redemption date: "+str(rdate))

token_ratio,hour = am.token_ratio(rdate)
tokenAmount = assetMass/token_ratio
print("    Token ratio: "+str("%.8f" % token_ratio)+" at hour "+str(hour))
print("    Required total tokens: "+str("%.8f" % (assetMass/token_ratio)))
print(" ")
inpt = input("Enter total number of burnt token types: ")
ntokens = int(inpt)
if ntokens < 1:
    print("ERROR: must have one or more tokens types to redeem")
    print("Exit")
    sys.exit()

burnt_tokens = []
for itt in range(ntokens):
    btoken = []
    print("    Burnt token "+str(itt)+": ")
    tokenid = input("        Enter token ID: ")
    inpt = input("        Enter amount: ")
    tamount = float(inpt)
    btoken.append(tokenid)
    btoken.append(tamount)
    btoken.append(map_obj.get_mass_tokenid(tokenid))
    burnt_tokens.append(btoken)

print(" ")
print("Perform token report and confirm burn")
#perform a token report to determine that the tokens have been successfully burnt
utxorep = ocean.call('getutxoassetinfo')
print("Retrieving UTXO report ...")
print(" ")
map_dict = map_obj.get_json()

for btoken in burnt_tokens:
    for entry in utxorep:
        asset = entry["asset"]
        if asset == btoken[0]:
            amount = entry["amountspendable"] + entry["amountfrozen"]
            print("    TokenID: "+str(asset))
            print("        Map mass = "+str(btoken[2]))
            print("        Chain mass = "+str("%.3f" % (amount*token_ratio)))
            print("        Redemption mass = "+str("%.3f" % (btoken[1]*token_ratio)))
            diffr = btoken[2]-amount*token_ratio-btoken[1]*token_ratio
            print("        Difference = "+str("%.3f" % diffr))
            print(" ")
            if diffr < 0.0:
                print("ERROR: Excess tokens on chain - check burn")
                print("Exit")
                sys.exit()
print(" ")
print("Token remapping")
map_orig = map_obj
success = map_obj.remap_assets(burnt_tokens,rref,rdate)
print(" ")
if not success:
    print("Exit - remapping failed")
    sys.exit()

print("Total mass: "+str("%.3f" % map_obj.get_total_mass()))
print(" ")
print("Create comparison report:")
print(" ")
am.diff_mapping(map_obj,map_orig)

inpt = input("Confirm diff data correct? ")
print(" ")
if str(inpt) != "Yes":
    print("Exit")
    sys.exit()

print(" ")
c1_privkey = open('c1_privkey.dat','r').read()
print("Add signature to mapping object:")
map_obj.clear_sigs()
map_obj.update_time()
map_obj.sign_db(c1_privkey,1)
print(" ")
print("Export partially signed mapping object")
print(" ")
print("     ps1_map.json")
map_obj.export_json("ps1_map.json")