#!/bin/bash
#this is a comment-the first line sets bash as the shell script

if pgrep -x "oceand" | grep -v pgrep >&-
then
	echo "Ocean server online"
	echo -e
else
	$HOME/ocean/src/oceand -datadir=$HOME/goldnode_main -v &
	echo "Ocean server starting..."
	sleep 2
	echo -e
	sleep 2
	BlockCount=$($HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getblockcount)
	echo "BlockCount =" "$BlockCount"
	osascript -e 'display notification "GoldNode has started with BlockCount '$BlockCount'" with title "GoldNode"'
fi
