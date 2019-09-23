#!/bin/bash
#this is a comment-the first line sets bash as the shell script

./Ocean_Start_DGLD_Node.command
echo ""
echo 'BlockchainInfo:'
$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getblockchaininfo
Blockcount=$($HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getblockcount)
osascript -e 'display notification "Blockcount '$Blockcount'" with title "GoldNode"'
