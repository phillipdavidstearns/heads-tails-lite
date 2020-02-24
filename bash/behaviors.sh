#!/bin/bash
BEHAVIOR=$1
echo $BEHAVIOR
ssh heads-tails-01 "sudo python3 /home/heads-tails/heads-tails/Python/behaviors.py -b $BEHAVIOR"
ssh heads-tails-02 "sudo python3 /home/heads-tails/heads-tails/Python/behaviors.py -b $BEHAVIOR"