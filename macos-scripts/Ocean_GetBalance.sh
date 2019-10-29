#!/bin/bash
#this is a comment-the first line sets bash as the shell script

echo 'DGLD Balance'
$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getbalance
Balance=$($HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getbalance)
osascript -e 'display notification "Balance Retrieved" with title "GoldNode"'
echo ""

# Confirm exit command
read -n 1 -s -r -p "Press any key to continue";