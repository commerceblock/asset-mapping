#!/bin/bash
#this is a comment-the first line sets bash as the shell script

clear
if pgrep -x "oceand" | grep -v pgrep >&-
then
	echo "Ocean server is running"
	echo -e
else
	echo "Ocean server starting..."
	echo -e
	$HOME/ocean/src/oceand -datadir=$HOME/goldnode_main -v &
	sleep 2
	echo "Blockchain Info:"
	echo -e
	$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getblockchaininfo
	osascript -e 'display notification "goldnode has started successfully" with title "GoldNode"'
fi
