#!/bin/bash

git add -A
git commit -am "quick updates"
git push
ssh heads-tails-01 'cd /home/heads-tails/heads-tails;git pull'
ssh heads-tails-02 'cd /home/heads-tails/heads-tails;git pull'
exit 0