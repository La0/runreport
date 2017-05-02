#!/bin/bash
cd src
celery -A runreport worker -B -l info --purge -n base
