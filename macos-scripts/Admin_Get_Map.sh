#!/bin/bash
#this is a comment-the first line sets bash as the shell script

cd $HOME/asset-mapping/tools;
python3 get_map.py;

# Confirm exit command
read -n 1 -s -r -p "Press any key to continue"