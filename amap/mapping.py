#!/usr/bin/env python

import time
import pybitcointools as bc
from mnemonic.mnemonic import Mnemonic
import binascii
import json
from datetime import datetime

def controller_keygen():
#function to generate a random mnemonic recovery phrase
#and in turn a private a public keys 
    entropy_hex = bc.random_key()
    entropy_bytes = entropy_hex.decode("hex")
    mnemonic_base = Mnemonic(language='english')
    recovery_phrase = mnemonic_base.to_mnemonic(entropy_bytes)
    seed = Mnemonic.to_seed(recovery_phrase)
    privkey = bc.sha256(seed)
    pubkey = bc.privkey_to_pubkey(privkey)
    return privkey, pubkey, recovery_phrase

def controller_recover_key(recovery_phrase):
#function to recover a public and private key pair from a mnemonic phrase
    mnemonic_base = Mnemonic(language='english')
    seed = Mnemonic.to_seed(recovery_phrase)
    privkey = bc.sha256(seed)
    pubkey = bc.privkey_to_pubkey(privkey)
    return privkey, pubkey

def tgr(rdate = datetime.now()):
    rate = 0.01
    dayzero = datetime(2018, 8, 30, 0, 1)
    days = (rdate-dayzero).days
    tgrf = (1.0 + rate)**(days/365.0)
    return tgrf


class ConPubKey(object):
#class for a public key object for the full list of controller public keys
    def __init__(self,n_multisig,m_multisig,pubkeylist):
#initiate the object with the multisig parameters and list of publc keys
        self.jsondata = {}
        self.jsondata["n"] = n_multisig
        self.jsondata["m"] = m_multisig
        self.jsondata["pubkeys"] = {}
        for it in range(len(pubkeylist)):
            print(it)
            print(pubkeylist[it])
            self.jsondata["pubkeys"][it+1] = pubkeylist[it]

    def load_json(self,filename):
#read the list from a json file
        with open(filename) as file:
            self.jsondata = json.load(file)

    def export_json(self,filename):
#export the list as a json file
        with open(filename,'w') as file:
            json.dumps(self.jsondata,file)
            
    def load_genesis(self):
#connect to the ocean sidechain client and load the pubkey list
#from the genesis block of the sidechain
        print("loading pubkeylist from ocean rpc")
    
    def print_keys(self):
#print the pubkey json object
        print json.dumps(self.jsondata,sort_keys=True,indent=4)
    
    def list_keys(self):
#return the pubkeys as a list
        list = []
        numkeys = len(self.jsondata["pubkeys"])
        for it in range(numkeys):
            list.append(self.jsondata["pubkeys"][it+1])
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
        
    def add_asset(self,asset_ref,year_ref,mass,tokenid,location):
#add a new asset to the object
#a new entry number is determined
        maxasnum = 1
        for key in self.map["assets"]:
            if key > maxasnum: maxasnum = key
        ref = str(asset_ref)+'-'+str(year_ref)
#the reference is a concatination of the year and bar serial number
        self.map["assets"][maxasnum+1] = {}
        self.map["assets"][maxasnum+1]["ref"] = ref
        self.map["assets"][maxasnum+1]["mass"] = mass
        self.map["assets"][maxasnum+1]["tokenid"] = tokenid
        self.map["assets"][maxasnum+1]["location"] = location

    def remove_asset(self,asset_reference):
#function to remove a paticular asset reference from the object
        rmasset = []
        for i,j in self.map["assets"].items():
            if j["ref"] == asset_reference:
                rmasset.append(i)
                for num in rmasset:
                    del self.map["assets"][num]

    def verify_multisig(self,controller_pubkeys):
#function to verify the signatures of the object against the policy
#and supplied public key list: returns validity
        nsig = len(self.map["sigs"])
        if nsig <= self.map["n"]:
            print("Error: insufficient signatures")
            return 0
#the signature is generated over the asset list json object concatinated with the policy and time
        jsonstring = json.dumps(self["assets"].maps,sort_keys=True)
        jsonstring += str(self.map["n"]) + str(self.map["m"]) + str(self.map["time"])
        strhash = bc.sha256(jsonstring)
        nvalid = 0
#check all possible combinations of public keys and signatures
        for key in controller_pubkeys.list_keys():
            for it in range(nsig):
                sig = self.map["sigs"][it+1]
                if bc.ecdsa_verify(hash,sig,key): nvalid += 1
        if nvalid >= self.map["n"]:
            return True
        else:
            return False

    def verify_blockchain_commitment(self,commit):
#function to verify the hash of the entire object
        jsonstring = json.dumps(self.maps,sort_keys=True)
        strhash = bc.sha256(jsonstring)
        return commit == strhash

    def load_json(self,filename):
#load json object from file
        with open(filename) as file:
            self.map = json.load(file)

    def sign_db(self,privkey,index):
#function to add a signature to the mapping object generated from the supplied key
        jsonstring = json.dumps(self["assets"].maps,sort_keys=True)
        jsonstring += str(self.map["n"]) + str(self.map["m"]) +str(self.map["time"])
        strhash = bc.sha256(jsonstring)
        sig = bc.ecdsa_sign(strhash,privkey)
        self.map["sigs"][index] = sig

    def export_json(self,filename):
#function to save json object to file
        with open(filename,'w') as file:
            json.dumps(self.map,file)
        
    def get_json(self):
#retrieve and load json object from the public API
        print("retrieve json from public URL")

    def remap_assets(self,burnt_tokens,asset_reference,redemption_date):
        """
        remapping algorithm

        rtoken_array is an array of burnt tokens with corresponding amounts

        asset_reference is the reference ID of the redeemed asset

        the return value is an array of the remapped tokens
        """
#confirm redemption token values matches asset mass against tgr
        asset_mass = []
        total_mass = 0.0
        dtokens = []
        for i,j in self.map["assets"].items():
            if j["ref"] == asset_reference:
                asset_mass.append(j["mass"])
                total_mass += j["mass"]
                dtokens.append(j["tokenid"])
        
        total_tokens = 0.0
        for it in range(len(burnt_tokens)):
            total_tokens += burnt_tokens[it][1]
        
        if total_tokens < total_mass*tgr(redemption_date)/400.0:
            print("Error: insufficient tokens for asset redemption ")
            return False

        redemption_tolerance = 0.001
        if total_tokens > total_mass*tgr(redemption_date) + redemption_tolerance:
            print("Error: excess tokens for redemption")
            return False

#get the assets pointing to the burnt token array and reduce the masses
        btasset_list = []
        btasset_mass = []
        for it in range(len(burnt_tokens)):
            for i,j in self.map["assets"].items():
                if j["tokenid"] == burnt_tokens[it][0]:
                    btasset_list.append(j["ref"])
                    if j["mass"] > burnt_tokens[it][1]*400.0*tgr(redemption_date):
                        j["mass"] -= burnt_tokens[it][1]*400.0*tgr(redemption_date)
                        btasset_mass.append(burnt_tokens[it][1]*400.0*tgr(redemption_date))
                    else:
                        burnt_tokens[it][1] -= j["mass"]/(400*tgr(redemption_date))
                        btasset_mass.append(j["mass"])
                        j["mass"] = 0.0

#create new mappings for the dangling tokens. For each dangling token we add (or modify) a 
#an entry created from the the btasset_list


#remove the asset from the object
        rmasset = []
        for i,j in self.map["assets"].items():
            if j["ref"] == asset_reference:
                rmasset.append(i)
        for num in rmasset:
            del self.map["assets"][num]

        for num in rmlst:
            del self.map["assets"][num]


"""
So - for the asset that has been removed, we have a list of token ids that pointed to it (and the mass)
This is the dangling token list (in the first example this was a signle token but it could be multiple tokens). 

We also have a list of burnt token IDs (and the burn amounts) - each of these pointed to an asset. 
This is the dangling asset list. 

These first token IDs (that pointed to the removed asset) then need to point to the assets corresponding to the burnt tokens. 

So we need to match up the dangling token list with the dangling asset list. 

Initially, the dangling assets need to be modified to correct the loss of tokens (this requires these entries to be modified to reduce the mass associated with the burnt tokens. 

Each correction, then needs to be made up with a new entry, taking the reduced mass from the previous step, and linking it to the token ids left dangling from the removed asset. 

Need to take care of: token ids pointing to multiple assets, and asset ids pointing to multiple tokens. 
"""


    def upload_json(self):
#function to upload the json object to the public url
        print("upload json to public url")

    def get_total_mass(self):
#function to return the total mass of all assets listed in the object
        tmass = 0.0
        for it in range(len(self.map["assets"])):
            tmass += self.map["assets"][it+1]["mass"]
        return tmass

    def get_mass_tokenid(self,tokenid):
#function to return the total mass relating to a specific token ID
        tmass = 0.0
        for it in range(len(self.map["assets"])):
            if self.map["assets"][it+1]["tokenid"] == tokenid:
                tmass += self.map["assets"][it+1]["mass"]
        return tmass

    def get_mass_assetid(self,assetid):
#function to return the total mass relating to a specific asset ID
        tmass = 0.0
        for it in range(len(self.map["assets"])):
            if self.map["assets"][it+1]["ref"] == assetid:
                tmass += self.map["assets"][it+1]["mass"]
        return tmass

def diff_mapping(mapping_object_new,mapping_object_old):
    "this function compares two mapping objects and lists the changes"
