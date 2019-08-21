#!/usr/bin/env python

import boto3

print("Upload redeem list")

print("Upload to S3")
s3 = boto3.resource('s3')
s3.Object('cb-mapping','rassets.json').put(Body=open('rassets.json','rb'),ACL='public-read',ContentType='application/json')
