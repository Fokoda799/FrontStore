import logging

import requests

from django.shortcuts import render

logger = logging.getLogger(__name__)


def say_hello(request):
    try:
        logger.info("Calling httpbin...")
        response = requests.get("https://httpbin.org/delay/2")
        data = response.json()
        logger.info("Response received!")
    except requests.ConnectionError:
        logger.critical("httpbin is offline")
    return render(request, "index.html", {"data": data})
