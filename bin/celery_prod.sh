#!/bin/bash
celery -A coach worker -B -l info --purge
