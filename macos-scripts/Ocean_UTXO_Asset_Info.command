#!/bin/bash
#this is a comment-the first line sets bash as the shell script

clear
echo 'UTXO Asset Info'
$HOME/ocean/src/ocean-cli -datadir=$HOME/goldnode_main getutxoassetinfo
exit;