#!/bin/bash
#this is a comment-the first line sets bash as the shell script

if pgrep -x "oceand" | grep -v pgrep >&-
then
	echo "Ocean server already online"
	echo -e
else
	$HOME/ocean/src/oceand -datadir=$HOME/goldnode_main -v &
	echo "Ocean server starting..."
	echo -e
	sleep 2
	blockcount=$($HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getblockcount)
	sleep 2
	echo "Blockcount =" "$blockcount"
	osascript -e 'display notification "GoldNode has started with Blockcount '$blockcount'" with title "GoldNode"'
	exit
fi

# Confirm exit command
echo ""
read -n 1 -s -r -p "Press any key to continue";