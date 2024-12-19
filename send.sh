#!/bin/bash
echo "🟠 Running send.sh ..."i
# Random sleep between 1 and 9 minutes
# https://stackoverflow.com/questions/9049460/cron-jobs-and-random-times-within-given-hours
sleep ${RANDOM:0:1}m

cd $HOME/PhotosToSocial
source .venv/bin/activate
python main.py --send
echo "🟢 send.sh finished"
