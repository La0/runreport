#!/bin/bash
celery -A coach worker -B -l info --autoreload --purge
