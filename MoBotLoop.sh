#!/bin/bash

cd ~/Desktop/GTA\ Stuff/Bots/MoBot/MoBot

while :
do
	python3 MoBotLoop.py
	echo "\n"
	echo "Sleeping for 5 seconds..."
	count=5
	while [ $count -gt -1 ]
	do
		sleep 1
		echo $count
		count=$((count - 1))
	done
done
