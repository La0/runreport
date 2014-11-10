#!/bin/bash
celery -A coach worker -l info -Q tracks -n tracks
