#!/usr/bin/env python

from time
import pybitcointools as bc
from mnemonic.mnemonic import Mnemonic
import binascii
import json

def controller_keygen():
    entropy_hex = bc.random_key()
    entropy_bytes = entropy_hex.decode("hex")
    mnemonic_base = Mnemonic(language='english')
    recovery_phrase = mnemonic_base.to_mnemonic(entropy_bytes)
    seed = Mnemonic.to_seed(recovery_phrase)
    privkey = bc.sha256(seed)
    pubkey = bc.privkey_to_pubkey(privkey)
    return privkey, pubkey, recovery_phrase

def controller_recover_key(recovery_phrase):
    mnemonic_base = Mnemonic(language='english')
    seed = Mnemonic.to_seed(recovery_phrase)
    privkey = bc.sha256(seed)
    pubkey = bc.privkey_to_pubkey(privkey)
    return privkey, pubkey




class ConPubKey(object):
    
    def __init__(self,n_multisig,m_multisig,pubkeylist):
        self.jsondata = {}
        self.jsondata["n"] = n_multisig
        self.jsondata["m"] = m_multisig
        self.jsondata["pubkeys"] = {}
        it = 1
        for keys in pubkeylist:
            self.jsondata["pubkeys"][it] = pubkeylist[it-1]

    def load_json(filename):
        with open(filename) as file:
            self.jsondata = json.load(file)

    def export_json(filename):
        with open(filename,'w') as file:
            json.dumps(self.jsondata,file)
            
    def load_genesis(self):
        print("loading pubkeylist from ocean rpc")
    
    def print(self):
        print json.dumps(self.jsondata,sort_keys=True,indent=4)
    
    def list_keys(self):
        list = []
        numkeys = len(self.jsondata["pubkeys"])
        for it in range(numkeys)
            list.append(self.jsondata["pubkeys"][it+1])
        return list


class MapDB(object):

    def __init__(self,n_multisig,m_multisig):
        self.map = {}
        self.map["n"] = n_multisig
        self.map["m"] = m_multisig
        self.map["assets"] = {}
        self.map["sigs"] = {}
        self.map["time"] = time.time()
        
    def add_asset(self,asset_ref,year_ref,mass,tokenid,location):
        nassets = len(map["assets"])
        ref = str(asset_ref)+'-'+str(year_ref)
        self.map["assets"][nassets+1] = {}
        self.map["assets"][nassets+1]["ref"] = ref
        self.map["assets"][nassets+1]["mass"] = mass
        self.map["assets"][nassets+1]["tokenid"] = tokenid
        self.map["assets"][nassets+1]["location"] = location
        
    def verify_multisig(self,controller_pubkeys):
        nsig = len(self.map["sigs"])
        if nsig <= self.map["n"]:
            print("Error: insufficient signatures")
            return 0
        jsonstring = json.dumps(self["assets"].maps,sort_keys=True)
        jsonstring += str(self.map["n"]) + str(self.map["m"]) + str(self.map["time"])
        strhash = bc.sha256(jsonstring)
        nvalid = 0
        for key in controller_pubkeys.list_keys():
            for it in range(nsig):
                sig = self.map["sigs"][it+1]
                if bc.ecdsa_verify(hash,sig,key): nvalid += 1
        if nvalid >= self.map["n"]:
            return True
        else:
            return False

    def verify_blockchain_commitment(self,commit):
        jsonstring = json.dumps(self.maps,sort_keys=True)
        strhash = bc.sha256(jsonstring)
        return commit == strhash

    def load_json(self,filename):
        with open(filename) as file:
            self.map = json.load(file)

    def sign_db(self,privkey,index):
        jsonstring = json.dumps(self["assets"].maps,sort_keys=True)
        jsonstring += str(self.map["n"]) + str(self.map["m"]) +str(self.map["time"])
        strhash = bc.sha256(jsonstring)
        sig = bc.ecdsa_sign(strhash,privkey)
        self.map["sigs"][index] = sig

    def export_json(self,filename):
        with open(filename,'w') as file:
            json.dumps(self.map,file)
        

    def get_json(self):
        print("retrieve json from public URL")

    def remap_assets(self,rtoken_array,asset_reference):
        """
        remapping algorithm

        rtoken_array is an array of burt tokens with corresponding amounts

        asset_reference is the reference ID of the redeemed asset

        the return value is an array of the remapped tokens
        """
        

    def upload_json(self):
        print("upload json to public url")

    def get_total_mass(self):
        tmass = 0.0
        for it in range(len(self.map["assets"])):
            tmass += self.map["assets"][it+1]["mass"]
        return tmass

    def get_mass_tokenid(self,tokenid):
        tmass = 0.0
        for it in range(len(self.map["assets"])):
            if self.map["assets"][it+1]["tokenid"] == tokenid:
                tmass += self.map["assets"][it+1]["mass"]
        return tmass

    def get_mass_assetid(self,assetid):
        tmass = 0.0
        for it in range(len(self.map["assets"])):
            if self.map["assets"][it+1]["ref"] == assetid:
                tmass += self.map["assets"][it+1]["mass"]
        return tmass

def diff_mapping(mapping_object_new,mapping_object_old):
    "this function compares two mapping objects and lists the changes"
