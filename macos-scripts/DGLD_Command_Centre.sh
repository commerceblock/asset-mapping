#!/bin/Bash

clear
printf '\033[8;65;90t'
cd $HOME/asset-mapping/macos-scripts

RED='\033[0;31m'
AMBER='\033[0;33m'
NC='\033[0m' # No Colour

while true; do
	clear
	echo "Welcome to the DGLD Command Launcher"
	echo ""

# First Block Timestamp - 20 minutes earlier than first official block
# echo -n "First Block Timestamp: "; date -u -r 1568701200 #GenesisBlock 

# Current date vs estimated date based on 1stblock/blocktime/blockheight
# echo -n "Current Timestamp Estimate from Genesis Block Timestamp: "; date -u -r 1568701200 -v +"$blockheight_node"M
# echo ""

# Current date
echo -n "Date: "
date -u 
echo ""

# Ocean Node Sync Status
echo -n "Ocean Node Status: "
oceandstatus=$(pgrep oceand | awk '{ print "Online" }' ) 
if test $oceandstatus > 0 ; 
then
	echo "Running"
	echo ""
	
	# DGLD explorer blockheight via API
	echo -n "DGLD Blockheight: "
	blockheight_exp=$(curl -s https://explorer.dgld.ch/api/info |\
	jq '.blockheight')
	echo -e $blockheight_exp
	echo ""

# Blockchain sync check from explorer api [+/- block sync tolerance level]
if
	[[ $blockheight_node == '' ]]; then blockheight_node=$"0"; fi
while (( $blockheight_node < $blockheight_exp ));
do
	printf "\033[5m${AMBER}Blockchain synchronising...${NC}\033[0m"
	blockheight_node=$($HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main/ getblockcount)
	echo -e $blockheight_node
	sleep 2
		# Local node blockheight
done
echo -n "Local Blockheight: "; echo $blockheight_node;
else printf "${RED}Node not running${NC}"; echo ""
fi


# Show Menu
echo ""
menu=$(ls -lh *.sh | awk '{ print ++lvalue, $9 }')
menucount=$(echo "$menu"|wc -l)
echo "$menu"
echo ""

# Menu ID Entry
echo "Choose item 1 to"$menucount" and press enter:"
read menuid
echo ""

# Exit clause
if [[ -z $menuid ]] ; then exec
elif [[ $menuid == "00" ]] ; then exit ; echo "Exiting DGLD Command Launcher"; echo ""; exit
elif ! (($menuid >= 1 && $menuid <= $menucount)) ; then exec
else

# Execute command file
exec=$(echo "$menu" | grep -w "$menuid" | awk '{ print $2 }')
./"$exec"
echo ""
read -n 1 -s -r -p "Press any key to continue"
clear
fi
done

