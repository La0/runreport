#!/bin/bash
celery -A coach worker -l info --autoreload --purge
