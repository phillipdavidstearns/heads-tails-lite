#!/bin/bash

echo $1
echo $2

if [[ -z $1  || -z $2 ]]; then
	echo "[!] insufficent arguments supplied"
	exit 1
fi

if [[ $1 = "stop" ]]; then
	echo "[+] stopping behavior $2"
elif [[ $1 = "start" ]]; then
	echo "[+] starting behavior $2"
else
	echo "[!] first argument must be \'start\' or \'stop\'"
	exit 1
fi

ansible-playbook --extra-vars "behavior=$2" behavior_$1.yml