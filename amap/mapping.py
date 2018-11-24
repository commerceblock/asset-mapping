#!/usr/bin/env python

import time
import bitcoin as bc
from mnemonic.mnemonic import Mnemonic
import binascii
import json
import calendar
import codecs
from datetime import datetime
from datadiff import diff

def controller_keygen():
#function to generate a random mnemonic recovery phrase
#and in turn a private a public keys
    decode_hex = codecs.getdecoder("hex_codec")
    entropy_hex = bc.random_key()
    entropy_bytes = decode_hex(entropy_hex)[0]
    mnemonic_base = Mnemonic(language='english')
    recovery_phrase = mnemonic_base.to_mnemonic(entropy_bytes)
    seed = Mnemonic.to_seed(recovery_phrase)
    privkey = bc.sha256(seed)
    pubkey = bc.privkey_to_pubkey(privkey)
    cpubkey = bc.compress(pubkey)
    return privkey, cpubkey, recovery_phrase

def controller_recover_key(recovery_phrase):
#function to recover a public and private key pair from a mnemonic phrase
    mnemonic_base = Mnemonic(language='english')
    seed = Mnemonic.to_seed(recovery_phrase)
    privkey = bc.sha256(seed)
    pubkey = bc.privkey_to_pubkey(privkey)
    cpubkey = bc.compress(pubkey)
    return privkey, cpubkey

def token_ratio(blockheight):
#function to return the token ratio at the supplied block height
#The rate is the inflation rate (not the demmurage rate)
    rate = 0.0101010101010101
#Hourly inflation rate
    hrate = (1.0 + rate)**(1.0/(365.0*24.0))
#The zero ratio is the token ratio at time zero
    zeroratio = 400.0
#calculate the number of hours based on the blockheight
    hours = blockheight // 60
#calculate the token ratio iteratively based on intermediate rounding to 8 deciaml places
    ratio = 1.0
    for it in range(hours):
        ratio += round(ratio*hrate - ratio,8)
    tr = zeroratio/ratio
    return round(tr,8)

class ConPubKey(object):
#class for a public key object for the full list of controller public keys
    def __init__(self,n_multisig=0,m_multisig=0,pubkeylist=[]):
#initiate the object with the multisig parameters and list of publc keys
        self.jsondata = {}
        self.jsondata["n"] = n_multisig
        self.jsondata["m"] = m_multisig
        self.jsondata["pubkeys"] = {}
        for it in range(len(pubkeylist)):
            self.jsondata["pubkeys"][it+1] = pubkeylist[it]

    def load_json(self,filename):
#read the list from a json file
        with open(filename) as file:
            self.jsondata = json.load(file)

    def export_json(self,filename):
#export the list as a json file
        with open(filename,'w') as file:
            json.dump(self.jsondata,file)
            
    def load_genesis(self):
#connect to the ocean sidechain client and load the pubkey list
#from the genesis block of the sidechain
        print("loading pubkeylist from ocean rpc")
    
    def print_keys(self):
#print the pubkey json object
        print(json.dumps(self.jsondata,sort_keys=True,indent=4))
    
    def list_keys(self):
#return the pubkeys as a list
        list = []
        for i,j in self.jsondata["pubkeys"].items():
            list.append(j)
        return list


class MapDB(object):
#class for the asset mapping object
    def __init__(self,n_multisig,m_multisig):
#initialise object and dict structure with multisig params
        self.map = {}
        self.map["n"] = n_multisig
        self.map["m"] = m_multisig
        self.map["assets"] = {}
        self.map["sigs"] = {}
        self.map["time"] = time.time()
        self.map["height"] = 0
        
    def add_asset(self,asset_ref,year_ref,mass,tokenid,manufacturer):
#add a new asset to the object
#a new entry number is determined
        maxasnum = 0
        for i,j in self.map["assets"].items():
            if int(i) > maxasnum: maxasnum = int(i)
        ref = str(asset_ref)+'-'+str(year_ref)+'-'+str(manufacturer)
#the reference is a concatination of the year and bar serial number and manufacturer
        for i,j in self.map["assets"].items():
            if j["ref"] == ref:
                print("Error: reference already used in mapping")
                return False

        self.map["assets"][str(maxasnum+1)] = {}
        self.map["assets"][str(maxasnum+1)]["ref"] = ref
        self.map["assets"][str(maxasnum+1)]["mass"] = mass
        self.map["assets"][str(maxasnum+1)]["tokenid"] = tokenid
        return maxasnum+1

    def update_time(self,ntime = time.time()):
#function to update the time-stamp of the object
        self.map["time"] = ntime

    def update_height(self,blockheight):
#function to updatde the block-height
        self.map["height"] = blockheight

    def get_time(self):
#return the timestamp of the object
        return self.map["time"]

    def get_height(self):
#return the blockheight of the object
        return self.map["height"]

    def remove_asset(self,asset_reference):
#function to remove a paticular asset reference from the object
        rmasset = []
        count = 0
        for i,j in self.map["assets"].items():
            if j["ref"] == asset_reference:
                rmasset.append(i)
                count += 1
        if count == 0:
            print("Error: asset reference not present in object")
            return False
        for num in rmasset:
            del self.map["assets"][num]
        return True

    def verify_multisig(self,controller_pubkeys):
#function to verify the signatures of the object against the policy
#and supplied public key list: returns validity
        nsig = len(self.map["sigs"])
        if nsig < self.map["n"]:
            print("Error: insufficient signatures")
            return False
#the signature is generated over the asset list json object concatinated with the policy and time
        jsonstring = json.dumps(self.map["assets"],sort_keys=True)
        jsonstring += str(self.map["n"]) + str(self.map["m"]) + str(self.map["time"]) + str(self.map["height"])
        strhash = bc.sha256(jsonstring)
        nvalid = 0
#check all possible combinations of public keys and signatures
        for key in controller_pubkeys:
            for i,j in self.map["sigs"].items():
                if bc.ecdsa_verify(strhash,j,key): nvalid += 1
        if nvalid >= self.map["n"]:
            return True
        else:
            return False

    def verify_blockchain_commitment(self,commit):
#function to verify the hash of the entire object
        jsonstring = json.dumps(self.map,sort_keys=True)
        strhash = bc.sha256(jsonstring)
        return commit == strhash

    def load_json(self,filename):
#load json object from file
        with open(filename) as file:
            self.map = json.load(file)

    def sign_db(self,privkey,index):
#function to add a signature to the mapping object generated from the supplied key
        jsonstring = json.dumps(self.map["assets"],sort_keys=True)
        jsonstring += str(self.map["n"]) + str(self.map["m"]) +str(self.map["time"]) + str(self.map["height"])
        strhash = bc.sha256(jsonstring)
        sig = bc.ecdsa_sign(strhash,privkey)
        self.map["sigs"][index] = sig

    def clear_sigs(self):
        self.map["sigs"].pop("1", None)
        self.map["sigs"].pop("2", None)
        self.map["sigs"].pop("3", None)

    def export_json(self,filename):
#function to save json object to file
        with open(filename,'w') as file:
            json.dump(self.map,file)

    def print_json(self):
#function to output the full json object
        print(json.dumps(self.map,sort_keys=True,indent=4))

    def get_json(self):
        return self.map
        
    def download_json(self):
#retrieve and load json object from the public API
        print("retrieve json from public URL")

    def remap_assets(self,burnt_tokens,asset_reference,redemption_height):
        """
        remapping algorithm

        rtoken_array is an array of burnt tokens with corresponding amounts

        asset_reference is the reference ID of the redeemed asset

        the return value is an array of the remapped tokens
        """
        #confirm redemption token values matches asset mass against token ratio
        tratio = token_ratio(redemption_height)

        dasset_mass = []
        total_mass = 0.0
        dtokens = []
        for i,j in self.map["assets"].items():
            if j["ref"] == asset_reference:
                dasset_mass.append(j["mass"])
                total_mass += j["mass"]
                dtokens.append(j["tokenid"])
        
        total_tokens = 0.0
        for it in range(len(burnt_tokens)):
            total_tokens += burnt_tokens[it][1]
        
        if round(total_tokens,8) < round(total_mass/tratio,8):
            print("Total tokens: "+str("%.8f" % total_tokens))
            print("Total converted mass: "+str(round(total_mass/tratio,8)))
            print("Error: insufficient tokens for asset redemption ")
            return False

        redemption_tolerance = 0.000001
        if total_tokens > tratio + redemption_tolerance:
            print("Error: excess tokens for redemption")
            return False

        #get the assets pointing to the burnt token array and reduce the masses
        btasset_list = []
        btasset_mass = []
        for it in range(len(burnt_tokens)):
            for i,j in self.map["assets"].items():
                if j["tokenid"] == burnt_tokens[it][0]:
                    btasset_list.append(j["ref"])
                    if j["mass"] > burnt_tokens[it][1]*tratio:
                        j["mass"] -= round(burnt_tokens[it][1]*tratio,3)
                        btasset_mass.append(round(burnt_tokens[it][1]*tratio,3))
                    else:
                        burnt_tokens[it][1] -= j["mass"]/tratio
                        btasset_mass.append(j["mass"])
                        j["mass"] = 0.0

        #create new mappings for the dangling tokens. For each dangling token we add (or modify) a 
        #an entry created from the the btasset_list
        new_map = []
        bt_it = 0
        for it in range(len(dtokens)):
            if btasset_mass[bt_it] >= dasset_mass[it]:
                new_entry = []
                new_entry.append(dtokens[it])
                new_entry.append(btasset_list[bt_it])
                new_entry.append(dasset_mass[it])
                btasset_mass[bt_it] -= dasset_mass[it]
                new_map.append(new_entry)
            else:
                for it2 in range(len(btasset_list)):
                    new_entry = []
                    new_entry.append(dtokens[it])
                    new_entry.append(btasset_list[bt_it])
                    if btasset_mass[bt_it] <= dasset_mass[it]:
                        new_entry.append(btasset_mass[bt_it])
                        dasset_mass[it] -= btasset_mass[bt_it]
                        bt_it += 1
                        new_map.append(new_entry)
                    else:
                        new_entry.append(dasset_mass[it])
                        btasset_mass[bt_it] -= dasset_mass[it]
                        new_map.append(new_entry)
                        break
                    if bt_it == len(btasset_list): break

#update the mapping object with the new mappings: if a mapping already exists then modify it
#if a mapping is new, then create a new entry. 

        for entry in new_map:
            if entry[2] < 0.0:
                print("Error: negative mass after re-mapping")
                return False
            cntr = 0
            maxasnum = 1
            for i,j in self.map["assets"].items():
                if int(i) > maxasnum: maxasnum = int(i)
                if j["ref"] == entry[1] and j["tokenid"] == entry[0]:
                    if cntr >= 1:
                        print("Error: repeated asset-token mapping in object")
                        return False
                    j["mass"] += entry[2]
                    cntr += 1
            if cntr == 0:
                self.map["assets"][str(maxasnum+1)] = {}
                self.map["assets"][str(maxasnum+1)]["ref"] = entry[1]
                self.map["assets"][str(maxasnum+1)]["mass"] = entry[2]
                self.map["assets"][str(maxasnum+1)]["tokenid"] = entry[0]

#remove the redeemed asset from the object
        rmasset = []
        for i,j in self.map["assets"].items():
            if j["ref"] == asset_reference:
                rmasset.append(i)
        for num in rmasset:
            del self.map["assets"][num]

        return True

    def upload_json(self):
#function to upload the json object to the public url
        print("upload json to public url")

    def get_total_mass(self):
#function to return the total mass of all assets listed in the object
        tmass = 0.0
        for i,j in self.map["assets"].items():
            tmass += j["mass"]
        return tmass

    def get_mass_tokenid(self,tokenid):
#function to return the total mass relating to a specific token ID
        tmass = 0.0
        for i,j in self.map["assets"].items():
            if j["tokenid"] == tokenid:
                tmass += j["mass"]
        return tmass

    def get_mass_assetid(self,assetid):
#function to return the total mass relating to a specific asset ID
        tmass = 0.0
        for i,j in self.map["assets"].items():
            if j["ref"] == assetid:
                tmass += j["mass"]
        return tmass

def diff_mapping(mapping_object_new,mapping_object_old):
#function to compare two mapping objects and lists the changes
    print(diff(mapping_object_new.get_json(),mapping_object_old.get_json()))
