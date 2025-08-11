from django.contrib import admin
from .models import PredictionJob

@admin.register(PredictionJob)
class PredictionJobAdmin(admin.ModelAdmin):
    list_display = ("id", "text","status","result", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("text", "result")
