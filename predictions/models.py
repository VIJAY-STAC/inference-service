import uuid
from django.db import models

class PredictionJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("done", "Done"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    result = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
