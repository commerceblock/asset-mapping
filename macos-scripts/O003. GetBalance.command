#!/bin/bash
#this is a comment-the first line sets bash as the shell script
./ocean/src/ocean-cli -datadir=./goldnode_main getbalance
osascript -e 'display notification "Balance Retrieved" with title "GoldNode"'
exit;
