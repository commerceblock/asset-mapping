#!/usr/bin/env python                                              
import amap.mapping as am
import pybitcointools as bc
from datetime import datetime

map_obj = am.MapDB(2,3)
map_obj.load_json('map.json')

map_obj.print_json()

print("Redemption of asset: 757628-2016-Acme")
print("  Mass: 400.031")
rdate = datetime(2018, 9, 7, 0, 2)
print("  Redemption date: "+str(rdate))
print("              TGR: "+str(am.tgr(rdate)))
print("  Required tokens: "+str(am.tgr(rdate)*400.031/400))
print(" ")
print("Burnt tokens")
print("  aca8a14cf814d3c7fa5718df157a2229188eef435e45360558ce5a42893979e3: 0.3219832")
print("  6948440932e9544033f985fcca54615babfdfc8e4cac50e76dba468031131c36: 0.678312377")

btoken1 = []
btoken1.append("aca8a14cf814d3c7fa5718df157a2229188eef435e45360558ce5a42893979e3")
btoken1.append(0.321983253)
btoken2 = []
btoken2.append("6948440932e9544033f985fcca54615babfdfc8e4cac50e76dba468031131c36")
btoken2.append(0.678312377)

burnt_tokens = []
burnt_tokens.append(btoken1)
burnt_tokens.append(btoken2)

print("Total mass: "+str(map_obj.get_total_mass()-400.031))

print("Token remapping")

map_obj.remap_assets(burnt_tokens,"757628-2016-Acme",rdate)

map_obj.print_json()

print("Total mass: "+str(map_obj.get_total_mass()))

print map_obj.get_mass_tokenid("3077bed1525464237147bb7363f23f6f18bbe2a9d26f615c5a9a7aac08c8608d")
