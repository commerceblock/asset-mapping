#!/usr/bin/env python

import amap.mapping as am
import json
import os

print("Generate controller keys and recovery phrase")
print(" ")

#key file directory
keydir = os.getenv('KEYDIR', default="/Users/ttrevethan/asset-mapping/confirmer/keys/")

#object directory for import and export of json objects
objdir = os.getenv('OBJDIR', default="/Users/ttrevethan/asset-mapping/confirmer/obj/")

print("Generate new key-pair for controller:")
c1_private,c1_public,c1_recovery = am.controller_keygen()
print(" ")

print("  Private key written to privkey.dat in directory "+keydir)
print("  Public key written to pubkey.dat in directory "+objdir)
print("  Public key: "+c1_public)
print("  Recovery phrase: "+c1_recovery)
print(" ")
print("WRITE DOWN THE RECOVERY PHRASE AND STORE IN A SECURE LOCATION")
print(" ")
print("Copy the pubkey.dat file to a USB memory stick and send to CommerceBlock")
key_file = open(keydir+"privkey.dat","w")
key_file.write(c1_private)
key_file.close()

pubkey_file = open(objdir+"pubkey.dat","w")
pubkey_file.write(c1_public)
pubkey_file.close()

print(" ")
