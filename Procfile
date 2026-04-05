web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn frontstore.wsgi --bind 0.0.0.0:$PORT
celery: celery -A frontstore worker --uid=nobody -E