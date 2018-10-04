#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
from datetime import datetime
import amap.rpchost as rpc
import json

print("Issue an asset: 2-of-3 controller multisig")

print(" ")
print("Controller 1")
print(" ")

print("Controller 1: Load the mapping object")

map_obj = am.MapDB(2,3)
map_obj.load_json('map.json')
fmass = map_obj.get_total_mass()
print("    Total mass: "+str(fmass))
print(" ")

print("Controller 1: Load the P2SH address file")

with open('p2sh.json','r') as file:
    p2sh = json.load(file)

print(" ")

print("     Connecting to Ocean client")
print(" ")
rpcport = 18884
rpcuser = 'user1'
rpcpassword = 'password1'
url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
ocean = rpc.RPCHost(url)

print("     Specify issuance address and reissuance token address")
inpt = input("        Enter issuance address:")
issueToAddress = str(inpt)
inpt = input("        Enter reissuance address:")
reissuanceToken = str(inpt)
print("        Issuance address: "+issueToAddress)
print("        Reissuance token: "+reissuanceToken)

print("     Specify asset reference data: ")
inpt = input("        Enter serial number:")
assetRef = str(inpt)
inpt = input("        Enter year of manufacture:")
assetYear = str(inpt)
inpt = input("        Enter manufacturer:")
assetMan = str(inpt)
inpt = input("        Enter fine mass:")
assetMass = float(inpt)

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

print("     Determine token issuance on "+str(datetime.now()))
tgr,hour = am.tgr()
tokenAmount = assetMass/tgr
print("        hour = "+str(hour))
print("        tokens = "+str(tokenAmount))
print(" ")

print("     Create raw issuance transaction:")
fee = 0.0001
print("        Retrieve policy asset UTXO from the database:")
#the UTXO database lists unspent policy asset outputs that can be used for issuance
#each line lists the txid, the vout, the value of the output and scriptPubKey
with open("policyTxOut.dat") as file:
    utxolist = file.readlines()
utxolist = [x.strip() for x in utxolist]
txin = utxolist[0].split()
print("            TxID: "+txin[0]+" vout: "+txin[1])
print("            Ammount: "+txin[2])
print(" ")
changeAmount = float(txin[2])-fee
issuancetx = ocean.call('createrawissuance',issueToAddress,str("%.8f" % tokenAmount),reissuanceToken,'1',p2sh["address"],str("%.8f" % changeAmount),1,str("%.8f" % fee),txin[0],str(int(txin[1])))
print("        Token ID: "+issuancetx["asset"])
print(" ")

print("     Add entry to object:")
map_obj.add_asset(assetRef,assetYear,assetMass,issuancetx["asset"],assetMan)
map_obj.update_time()
tmass = map_obj.get_total_mass()
print("            New total mass: "+str(tmass))

print(" ")

print("     Add partial signature to issuance transaction:")
c1_privkey = open('c1_privkey.dat','r').read()
#version byte is 239 for ocean regtest mode
version_byte = 239-128
#encode private key to be importable to ocean client
c1_pk_wif = bc.encode_privkey(c1_privkey,'wif_compressed',version_byte)

partial_sig_tx = ocean.call('signrawtransaction',issuancetx["rawtx"],[{"txid":txin[0],"vout":int(txin[1]),"scriptPubKey":txin[3],"redeemScript":p2sh["redeemScript"]}],[c1_pk_wif])
print("     Add signature to mapping object:")
map_obj.sign_db(c1_privkey,1)
print(" ")
print("     Export partially signed data objects")
map_obj.export_json("ps1_map.json")
#add the input transaction data to the tx file to enable the second signature to be generated
partial_sig_tx["scriptPubKey"] = txin[3]
partial_sig_tx["txid"] = txin[0]
partial_sig_tx["vout"] = txin[1]
with open("ps1_tx.json",'w') as file:
          json.dump(partial_sig_tx,file)
