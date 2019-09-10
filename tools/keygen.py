#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
import json
import os

print("Generate single wallet key pair")
print(" ")

print("Generate new key-pair:")
c1_private,c1_public,c1_recovery = am.controller_keygen()
print(" ")

print("  DGLD encoded private key written to wallet_privkey.dat")
print("  Public key written to wallet_pubkey.dat")
print("  Public key: "+c1_public)
print("  Recovery phrase: "+c1_recovery)
print(" ")
print("WRITE DOWN THE RECOVERY PHRASE AND STORE IN A SECURE LOCATION")
print(" ")
print("Copy the wallet_pubkey.dat file to a USB memory stick and send to CommerceBlock")
encoded_privkey = bc.encode_privkey(c1_private,'wif_compressed',52)
key_file = open("privkey.dat","w")
key_file.write(encoded_privkey)
key_file.close()

pubkey_file = open("pubkey.dat","w")
pubkey_file.write(c1_public)
pubkey_file.close()

print(" ")
