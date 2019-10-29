#!/bin/bash
#this is a comment-the first line sets bash as the shell script

echo 'BlockchainInfo:'
$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getblockchaininfo
Blockcount=$($HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getblockcount)
osascript -e 'display notification "Blockcount '$Blockcount'" with title "GoldNode"'

# Confirm exit command
echo ""
read -n 1 -s -r -p "Press any key to continue";