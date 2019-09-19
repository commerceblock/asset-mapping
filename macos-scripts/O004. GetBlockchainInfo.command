#!/bin/bash
#this is a comment-the first line sets bash as the shell script
./ocean/src/ocean-cli -datadir=./goldnode_main/ getblockchaininfo
osascript -e 'display notification "Blockchain Information Retrieved" with title "GoldNode"'
exit;
