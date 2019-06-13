#!/usr/bin/env python

import amap.mapping as am
import json
import os

print("Generate Policy wallet (freezelist and burnlist) keys")
print(" ")

print("Generate key-pair for freezelist wallet:")
c1_private,c1_public,c1_recovery = am.controller_keygen()
print(" ")

print("  Freezelist private key written to frzlist_privkey.dat")
print("  Freezelist public key written to frzlist_pubkey.dat")
print("  Public key: "+c1_public)
print("  Recovery phrase: "+c1_recovery)
print(" ")
print("WRITE DOWN THE RECOVERY PHRASE AND STORE IN A SECURE LOCATION")
print(" ")
print("Generate key-pair for burnlist wallet:")
c2_private,c2_public,c2_recovery = am.controller_keygen()
print(" ")
print("  Burnlist private key written to brnlist_privkey.dat")
print("  Burnlist public key written to brnlist_pubkey.dat")
print("  Public key: "+c2_public)
print("  Recovery phrase: "+c2_recovery)
print(" ")
print("WRITE DOWN THE RECOVERY PHRASE AND STORE IN A SECURE LOCATION")
print(" ")
print("Copy the brnlist_pubkey.dat and frzlist_pubkey.dat files to a USB memory stick and send to CommerceBlock")
key_file = open("frzlist_privkey.dat","w")
key_file.write(c1_private)
key_file.close()

pubkey_file = open("frzlist_pubkey.dat","w")
pubkey_file.write(c1_public)
pubkey_file.close()

key_file = open("brnlist_privkey.dat","w")
key_file.write(c2_private)
key_file.close()

pubkey_file = open("brnlist_pubkey.dat","w")
pubkey_file.write(c2_public)
pubkey_file.close()

print(" ")
