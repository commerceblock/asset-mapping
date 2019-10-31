#!/bin/bash
#this is a comment-the first line sets bash as the shell script

if pgrep -x "oceand" | grep -v pgrep >&-
then
	echo ""
else
$HOME/ocean/src/oceand -datadir=$HOME/goldnode_main -v &
sleep 2
fi
