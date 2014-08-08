#!/bin/bash
celery -A coach worker -l info -Q garmin
