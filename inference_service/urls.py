from django.contrib import admin
from django.urls import path
from predictions.views import PredictView, PredictStatusView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('predict', PredictView.as_view(), name='predict'),
    path('predict/<uuid:job_id>', PredictStatusView.as_view(), name='predict_status'),
]
