#!/bin/bash
#this is a comment-the first line sets bash as the shell script

echo 'UTXO Asset Info'
$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getutxoassetinfo

# Confirm exit command
echo ""
read -n 1 -s -r -p "Press any key to continue";