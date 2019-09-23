#!/bin/bash

clear

while true; do
	echo "Enter Blockheight for Blockhash"
	read Blockheight
	if test $Blockheight == "exit"; then break
else
	$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getblockhash $Blockheight &
	Blockhash=$($HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getblockhash $Blockheight)
	osascript -e 'display notification "Blockhash: '$Blockhash'" with title "GoldNode"'
	echo ""
fi
done
