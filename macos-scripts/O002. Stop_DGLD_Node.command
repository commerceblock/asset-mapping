#!/bin/bash
#this is a comment-the first line sets bash as the shell script
./ocean/src/ocean-cli -datadir=./goldnode_main stop &
sleep 10
osascript -e 'display notification "goldnode has stopped successfully" with title "GoldNode"'
