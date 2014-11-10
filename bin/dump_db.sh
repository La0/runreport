#!/bin/bash
BASE=`readlink -f $( dirname "${BASH_SOURCE[0]}" )/..`
cd $BASE
source env/bin/activate

DUMP_PATH="$BASE/db/$(date +%Y%m%d).json"
APPS="sport users club page plan messages"

./manage.py dumpdata --indent=4 -e sessions $APPS > $DUMP_PATH
