#!/bin/bash
#this is a comment-the first line sets bash as the shell script

if pgrep -x "oceand" | grep -v pgrep >&-
then
	$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main stop
	sleep 2
	clear
	echo "Ocean server offline"
	osascript -e 'display notification "goldnode has stopped successfully" with title "GoldNode"'
else
	echo "Ocean server is not currently running"
	echo -e
fi
