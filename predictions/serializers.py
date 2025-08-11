from rest_framework import serializers
from .models import PredictionJob

class PredictionJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionJob
        fields = ["id", "text", "status", "result"]
        read_only_fields = ["id", "status", "result"]
