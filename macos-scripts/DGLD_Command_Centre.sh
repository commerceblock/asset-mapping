#!/bin/Bash

clear
printf '\033[8;65;90t'
cd $HOME/asset-mapping/macos-scripts
#./Ocean_Start_DGLD_Node.sh

RED='\033[0;31m'
NC='\033[0m' # No Color

while true; do
	clear
	echo "Welcome to the DGLD Command Launcher"
	echo ""

# First Block Timestamp - 20 minutes earlier than first official block
# echo -n "First Block Timestamp: "; date -u -r 1568701200 #GenesisBlock 

# Current date
echo -n "Current Date: "
date -u 
echo ""

# DGLD explorer blockheight via API
echo -n "DGLD Explorer Blockheight: "
blockheight_exp=$(curl -s https://explorer.dgld.ch/api/info -H 'cookie: __cfduid=de4c33e3c5a0639f0950ff48fd34daeec1566473055; wooTracker=y3S3DNZ133lc; onfido-js-sdk-woopra=VtFyaEMgZCRC; CF_Authorization=eyJhbGciOiJSUzI1NiIsImtpZCI6Ijc3ZTNjZDQyMjRhNTYzNTI0NWE5MTlkNzNlMjgzZGYxNzY2ZDcyMGEzYzEzMjUzMjhkOTAxOGRiOGM5YmVhM2MifQ.eyJhdWQiOlsiNmY3M2MyNmRkMmUzMGVlMDY5NDQwZDhiNmJhMTBjMmY3NTczNzBlNjM3MWNlNzJjNzYxOTE0NjNjNTdkN2U0ZSJdLCJlbWFpbCI6ImRhbi5ldmVAZ3RzYS5pbyIsImV4cCI6MTU3MDAyOTYxOSwiaWF0IjoxNTY5OTQzMjE5LCJuYmYiOjE1Njk5NDMyMTksImlzcyI6Imh0dHBzOi8vZGdsZC5jbG91ZGZsYXJlYWNjZXNzLmNvbSIsInR5cGUiOiJhcHAiLCJzdWIiOiIwNzM1RTI2RUIxQkQ4N0ExQjcyRDhBMEY3NTc2QzlBRkRFQkIyMUVCIn0.G8cIWqufv-pjAs5YogQReha5UZ9h0PcCaoHR73UQ2ZgixlIueH2IfKLHo8Gjf-QwtRpGupjcr8ABGSKgrCEg28S9BSbiUQ3AWzznU-8RqIWKBQWT0UDKMUkl4aPyLM3lBnt4QmGb8bqNLxP3_kNE-jOwen_89N51fKQ6yfNEtIbLoZtpGBbbZ672UaD1tB6GUk6rdY29M6P36z6Csf9Dqh2-WFsOc73HZ0yz0pJ0knmCBI9z7l_okLMwpFmxm7WKydi0wssqqgPcH4YBHw1ni2wv2AWHupuCRCTvdpk10HvfFOM7jwZ1EpCBwL49B94AeQbdDqyGhzkzI2yzCCcRHg'|\
jq '.blockheight')
# blockheight_exp=$'21294'
echo $blockheight_exp
echo ""

# Ocean Node Status
echo -n "Local Ocean Node Status: "
oceandstatus=$(pgrep oceand | awk '{ print "Online" }' ) 
if test $oceandstatus > 0 ; 
then
	echo "Running"
	echo ""

	# Current BlockHeight
	blockheight_node=$($HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main/ getblockcount)
	# blockheight_node=$'21291' # variable test
	# Local node blockheight
	echo -n "Local Node Blockheight: "; echo $blockheight_node;
	echo ""
else printf "${RED}Node is not running ${NC}";
	echo ""
fi

# Blockchain sync check from explorer api [+/- block sync tolerance level]
if [[ $blockheight_node == '' ]]; then blockheight_node=$"0"; fi
	echo -n "Sync Status: "
if (( $blockheight_node >= $blockheight_exp )); then echo -e "Blockchain synchronised"; else printf "${RED}Blockchain not yet synchronised ${NC}"  ; echo ""; fi

# Current date vs estimated date based on 1stblock/blocktime/blockheight
# echo -n "Current Timestamp Estimate from Genesis Block Timestamp: "; date -u -r 1568701200 -v +"$blockheight_node"M
# echo ""

# Show Menu
echo ""
menu=$(ls -lh *.sh | awk '{ print ++lvalue, $9 }')
echo "$menu"
echo ""

# Menuid entry
echo "Type menu number and press enter:"
read menuid
echo ""
if test $menuid == "000"; then exit
elif test $menuid == "999" ; then break $HOME/Command_Menu.sh
else
# Execute command file
exec=$(echo "$menu" | grep -w "$menuid" | awk '{ print $2 }')
./"$exec"
echo ""
read -n 1 -s -r -p "Press any key to continue"
clear
fi
done

