#!/usr/bin/env python                                              
import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import time
import boto3
import sys
import json
import requests

# Connecting to Ocean client
rpcport = 8332
rpcuser = 'ocean'
rpcpassword = 'oceanpass'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

# Redemption transaction backend process
def redemption_check(rref,rfeetx,rtx):

    # hard-coded address for the redemption fee and the required amount
    fAddress = "12tkJYZGHAbMprRPGwHGKtVFPMydND9waZ"
    rfee = 5.0

    #Load the mapping object - connecting to S3
    req = requests.get('https://s3.eu-west-1.amazonaws.com/gtsa-mapping/map.json')

    map_obj = am.MapDB(2,3)
    map_obj.init_json(req.json())

    #load the controller public keys
    con_keys = am.ConPubKey()
    con_keys.load_json('controllers.json')
    key_list = con_keys.list_keys()

    if not map_obj.verify_multisig(key_list):
        return False,"Signature verification failed"

    s3 = boto3.resource('s3')
    s3.Bucket('gtsa-mapping').download_file('rassets.json','rassets.json')

    # Load the redeem list object - rassets.json
    with open('rassets.json') as file:
        r_obj = json.load(file)

    chaininfo = ocean.call('getblockchaininfo')
    blkh = int(chaininfo["blocks"])
    token_ratio = am.token_ratio(blkh)

    rmass = map_obj.get_mass_assetid(rref)
    if rmass < 0.1:
        return False,"Invalid asset reference"

    inlist = 0
    locked = False
    for asst in r_obj["assets"]:
        if asst["ref"] == rref:
            inlist = 1
            locked = asst["lock"]

    if inlist == 0:
        return False, "Asset reference not in the redeemable asset list"

    if locked:
        return False, "Entered asset already locked for redemption"

    # expect number of tokens for redemption
    exptoken = am.token_amount(blkh,rmass)

    feetxcheck = ocean.call('testmempoolaccept',rfeetx)

    if feetxcheck["allowed"] == 0:
        return False, "Fee transaction invalid "+feetxcheck["reject-reason"]

    feedecode = ocean.call('decoderawtransaction',rfeetx)

    feetotal = 0.0
    for outs in feedecode["vout"]:
        if outs["scriptPubKey"]["type"] == "pubkeyhash":
            if outs["scriptPubKey"]["addresses"][0] == fAddress:
                feetotal += outs["value"]

    if feetotal < rfee:
        return False, "Fee transaction total tokens: "+str(feetotal)+" is insufficient"

    rtxcheck = ocean.call('testmempoolaccept',rtx)

    if rtxcheck["allowed"] == 0:
        return False, "Redemption transaction invalid "+rtxcheck["reject-reason"]

    rdecode = ocean.call('decoderawtransaction',rtx)

    frztag = 0
    tokentotal = 0.0
    rAddresses = []
    rAssets = []
    for outs in rdecode["vout"]:
        if map_obj.get_mass_tokenid(outs["asset"]) < 0.1:
            return False, "ERROR: redemption transaction contains an un-mapped token"
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
        return False, "Transaction is not a redemption transaction"

    if tokentotal < round(exptoken,6):
        return False, "Redemption transaction total tokens: "+str(feetotal)+" is insufficient"


    return True, "ALL REDEMPTION CHECKS PASSED"


# test function

rref = "123456-2018-Acme"

# open transaciton files
with open('rfee.dat', 'r') as file:
    rfeetx = file.read()

filenam = "rtx-"+rref+".dat"
with open(filenam, 'r') as file:
    rtx = file.read()

# run the redemption tx check function
rpass,message = redemption_check(rref,rfeetx,rtx)

print(message)
