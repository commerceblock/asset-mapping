#!/usr/bin/env python

import amap.mapping as am

print("Set-up keys for a 2-of-3 multisig controller policy")

controller_pub_keys = []

print("Generate keys for controller 1:")
c1_private,c1_public,c1_recovery = am.controller_keygen()

print("  C1 private key: "+c1_private)
print("  C1 public key: "+c1_public)
print("  C1 recovery phrase: "+c1_recovery)
controller_pub_keys.append(c1_public)
key_file = open("c1_privkey.dat","w")
key_file.write(c1_private)
key_file.close()
print(" ")

print("Generate keys for controller 2:")
c2_private,c2_public,c2_recovery = am.controller_keygen()

print("  C2 private key: "+c2_private)
print("  C2 public key: "+c2_public)
print("  C2 recovery phrase: "+c2_recovery)
controller_pub_keys.append(c2_public)
key_file = open("c2_privkey.dat","w")
key_file.write(c2_private)
key_file.close()
print(" ")

print("Generate keys for controller 3:")
c3_private,c3_public,c3_recovery = am.controller_keygen()

print("  C3 private key: "+c3_private)
print("  C3 public key: "+c3_public)
print("  C3 recovery phrase: "+c3_recovery)
controller_pub_keys.append(c3_public)
key_file = open("c3_privkey.dat","w")
key_file.write(c3_private)
key_file.close()
print(" ")

print("Creating controller object with 2 of 3 policy")
con_obj = am.ConPubKey(2,3,controller_pub_keys)

print("Exporting object to file")
con_obj.export_json('controllers.json')

print("Print object")
con_obj.print_keys()
