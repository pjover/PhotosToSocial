#!/bin/bash
echo "🟠 Running load.sh ..."i
cd $HOME/PhotosToSocial
source .venv/bin/activate
python main.py --load
echo "🟢 load.sh finished"
