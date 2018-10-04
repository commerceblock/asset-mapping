#!/usr/bin/env python

import amap.mapping as am
import amap.rpchost as rpc
import json

print("Set-up keys for a 2-of-3 multisig controller policy")
print(" ")

controller_pub_keys = []

print("Generate keys for controller 2:")
c2_private,c2_public,c2_recovery = am.controller_keygen()

print("  C2 private key: "+c2_private)
print("  C2 public key: "+c2_public)
print("  C2 recovery phrase: "+c2_recovery)
print(" ")

