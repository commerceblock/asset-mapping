#!/bin/bash

./Ocean_Start_DGLD_Node.sh

while true; do
	echo "Enter Blockheight for Blockhash"
	read blockheight
	if [[ -z $blockheight ]] ; then exec
	elif [[ $blockheight == "00" ]] ; then exit ; echo "Exiting DGLD Command Launcher"; echo ""; exit
	elif ! (($blockheight >= 0 && $blockheight <= $blockheight)) ; then exec
else
	$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getblockhash $blockheight &
	blockhash=$($HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getblockhash $blockheight)
	osascript -e 'display notification "Blockhash: '$blockhash'" with title "GoldNode"'
	echo ""
fi
done
