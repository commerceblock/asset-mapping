#!/bin/bash
#this is a comment-the first line sets bash as the shell script
./ocean/src/oceand -datadir=./goldnode_main &
sleep 16
osascript -e 'display notification "goldnode has started successfully" with title "GoldNode"'
./ocean/src/ocean-cli -datadir=./goldnode_main getblockchaininfo
exit
