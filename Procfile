release: python manage.py migrate
web: gunicorn frontstore.wsgi
worker: celery -A frontstore worker -l info --uid=nobody
