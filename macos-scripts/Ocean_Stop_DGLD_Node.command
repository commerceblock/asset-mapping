#!/bin/bash
#this is a comment-the first line sets bash as the shell script

clear
if pgrep -x "oceand" | grep -v pgrep >&-
then
	$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main stop
	sleep 2
	echo -e
	echo "Ocean server stopped"
	osascript -e 'display notification "goldnode has stopped successfully" with title "GoldNode"'
else
	echo "The ocean server is not currently running"
	echo -e
fi
