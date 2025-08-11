from django.urls import path
from .views import PredictView, PredictStatusView

urlpatterns = [
    path('predict/', PredictView.as_view(), name='predict'),
    path('predict/<uuid:job_id>/', PredictStatusView.as_view(), name='predict-status'),
]
