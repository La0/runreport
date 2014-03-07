#!/bin/bash
cd "$( dirname "${BASH_SOURCE[0]}" )/.."
source env/bin/activate
./manage.py publish_reports
