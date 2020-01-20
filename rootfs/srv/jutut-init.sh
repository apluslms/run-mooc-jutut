#!/bin/sh -eu

# Ensure LTI key
if ! setuidgid $USER python3 manage.py list_lti_keys -k testjutut 2>/dev/null | grep -qsF testjutut; then
    setuidgid $USER python3 manage.py add_lti_key -k testjutut -s testjutut -d "test key" 2>/dev/null
else
    setuidgid $USER python3 manage.py list_lti_keys -k testjutut 2>/dev/null
fi

# Start background services/tasks
start_services jutut-celery-worker jutut-celery-beat
