from django.urls import path, include
from django.contrib import admin
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok", "message": "Service is healthy"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('predictions.urls')),
    path('health/', health_check, name="health_check"), 
]
