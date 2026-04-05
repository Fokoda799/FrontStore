web: python manage.py migrate && gunicorn frontstore.wsgi
celery: celery -A frontstore worker --loglevel=info --uid=nobody