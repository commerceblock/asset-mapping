#!/bin/bash
#this is a comment-the first line sets bash as the shell script

cd /$HOME/asset-mapping/admin;
python3 redeem_process.py;

# Confirm exit command
echo ""
read -n 1 -s -r -p "Press any key to continue";