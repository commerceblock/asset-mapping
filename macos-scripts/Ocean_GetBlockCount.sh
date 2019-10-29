#!/bin/bash
#this is a comment-the first line sets bash as the shell script

echo 'BlockCount:'
$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main/ getblockcount

BlockCount=$($HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getblockcount)
osascript -e 'display notification "BlockCount '$BlockCount'" with title "GoldNode"'

# Confirm exit command
echo ""
read -n 1 -s -r -p "Press any key to continue";