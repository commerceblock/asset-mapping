#!/bin/bash
#this is a comment-the first line sets bash as the shell script
./ocean/src/ocean-cli -datadir=./goldnode_main/ getmempoolinfo
osascript -e 'display notification "MemPool Information Retrieved" with title "Mem Pool"'
