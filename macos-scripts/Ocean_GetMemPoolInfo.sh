#!/bin/bash
#this is a comment-the first line sets bash as the shell script

$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main/ getmempoolinfo
osascript -e 'display notification "MemPool Information Retrieved" with title "Mem Pool"'

# Confirm exit command
echo ""
read -n 1 -s -r -p "Press any key to continue";