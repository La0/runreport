#!/bin/bash
cd src
celery -A runreport worker -B -l info --autoreload --purge -n base
