#!/usr/bin/with-contenv /bin/sh
set -eu

cd /srv/jutut

# Use python from virtualenv if present
[ -e "/local/venv_jutut/bin/activate" ] && . /local/venv_jutut/bin/activate

# Ensure database state
init-django-db.sh jutut jutut /srv/jutut-setup.py

# With dev code, we need to rerun few init tasks
if [ -e requirements.txt ]; then
    python3 manage.py compilemessages -v0
fi
setuidgid jutut python3 manage.py collectstatic --noinput -v0

# Ensure LTI key
if ! setuidgid jutut python3 manage.py list_lti_keys -k testjutut 2>/dev/null | grep -qsF testjutut; then
    setuidgid jutut python3 manage.py add_lti_key -k testjutut -s testjutut -d "test key" 2>/dev/null
else
    setuidgid jutut python3 manage.py list_lti_keys -k testjutut 2>/dev/null
fi

# Start background services/tasks
start_services jutut-celery-worker jutut-celery-beat

# Execute main script
if [ "${1:-}" = "manage" ]; then
    shift
    exec setuidgid jutut python3 manage.py "$@"
elif [ "${1:-}" ]; then
    exec setuidgid jutut "$@"
else
    exec setuidgid jutut python3 manage.py runserver 0.0.0.0:8082
fi
