#!/bin/bash
 
# Use pgrep to find the PID of the Celery process
pid=$(pgrep -f 'celery -A modules.celery_config worker -l INFO --concurrency=10')
 
# Check if the PID was found
if [ -z "$pid" ]; then
    echo "Celery process not found."
else
    # Kill the process
    kill -9 $pid
    echo "Celery process with PID $pid has been stopped."
fi