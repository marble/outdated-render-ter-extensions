#!/bin/sh

cd /home/mbless/HTDOCS/render-ter-extensions

if [ -r "REBUILD_REQUESTED" ]; then

python 010_cronjob_get_new_from_ter.py

rm -I REBUILD_REQUESTED

fi
