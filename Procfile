web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn frontstore.wsgi
celery: celery -A frontstore worker --uid=nobody