#!/bin/bash
#this is a comment-the first line sets bash as the shell script

./Ocean_Start_DGLD_Node.command
echo 'DGLD Balance'
$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getbalance
Balance=$($HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getbalance)
osascript -e 'display notification "Balance Retrieved" with title "GoldNode"'
exit;