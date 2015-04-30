#!/bin/bash
supervisorctl stop runreport_tracks
ps auxww | grep 'celery -A coach worker' | grep -v grep | awk '{print $2}' |xargs kill -9
supervisorctl start runreport_tracks
