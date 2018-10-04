#!/usr/bin/env python

import amap.mapping as am
import amap.rpchost as rpc
import json

print("Set-up keys for a 2-of-3 multisig controller policy")
print(" ")

controller_pub_keys = []

print("Generate keys for controller 1:")
c1_private,c1_public,c1_recovery = am.controller_keygen()

print("  C1 private key: "+c1_private)
print("  C1 public key: "+c1_public)
print("  C1 recovery phrase: "+c1_recovery)
print(" ")

