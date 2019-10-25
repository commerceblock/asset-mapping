#!/bin/bash
#this is a comment-the first line sets bash as the shell script

# Stop node
if pgrep -x "oceand" | grep -v pgrep >&-
then
	$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main stop
	sleep 2
	echo ""
	if pgrep -x "oceand" | grep -v pgrep >&-; then echo "killall oceand";fi;
fi
# Start node and reindex
	$HOME/ocean/src/oceand -datadir=$HOME/goldnode_main -v --reindex=1 &
	echo "Ocean server reindexing. Please wait for node to sync"
	sleep 4