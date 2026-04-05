from django.http import JsonResponse

from .redis_health import check_redis_connection

# Create your views here.


def redis_health(request):
    result = check_redis_connection()
    status = 200 if result.get("ok") else 503
    return JsonResponse(result, status=status)
