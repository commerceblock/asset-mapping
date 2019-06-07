#!/usr/bin/env python

import amap.mapping as am
import amap.rpchost as rpc
import json

print("Generate controller keys and recovery phrase")
print(" ")

controller_pub_keys = []

print("Generate new key-pair for controller:")
c1_private,c1_public,c1_recovery = am.controller_keygen()
print(" ")

print("  Private key written to c_privkey.dat")
print("  Public key written to c_pubkey.dat")
print("  Public key: "+c1_public)
print("  Recovery phrase: "+c1_recovery)
key_file = open("c_privkey.dat","w")
key_file.write(c1_private)
key_file.close()

pubkey_file = open("c_pubkey.dat","w")
pubkey_file.write(c1_public)
pubkey_file.close()

print(" ")
