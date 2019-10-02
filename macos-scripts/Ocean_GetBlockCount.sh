#!/bin/bash
#this is a comment-the first line sets bash as the shell script

./Ocean_Start_DGLD_Node.sh

echo 'BlockCount:'
$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main/ getblockcount

BlockCount=$($HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getblockcount)
osascript -e 'display notification "BlockCount '$BlockCount'" with title "GoldNode"'
