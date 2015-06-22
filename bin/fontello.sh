#!/bin/bash

URL="http://fontello.com"
SESSION=$(curl -X POST -F "config=@front/font/config.json" $URL 2> /dev/null)

echo "Use editor on $URL/$SESSION"
