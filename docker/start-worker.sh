#!/bin/sh
set -e

export PYTHONPATH=/app

exec celery -A app.workers.tasks worker --loglevel=info
