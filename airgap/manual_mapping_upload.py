#!/usr/bin/env python

import amap.mapping as am
import bitcoin as bc
import amap.rpchost as rpc
import json
import time
import boto3
import sys
import os
from datetime import datetime

s3 = boto3.resource('s3')


#upload new map to S3
print("Uploading map.json to AWS")
print(" ")
s3.Object('gtsa-mapping','map.json').put(Body=open('map.json','rb'),ACL='public-read',ContentType='application/json')
print("Upload successful")
print(" ")
