#!/bin/bash
#this is a comment-the first line sets bash as the shell script

./Ocean_Start_DGLD_Node.command

clear
cd $HOME/asset-mapping/admin;
python3 freezelist.py;
exit;
