from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .models import PredictionJob

class InferenceFunctionTests(TestCase):
    @patch("predictions.views.pika.BlockingConnection")
    def test_inference_function_mock_model(self, mock_connection):
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel
        job = PredictionJob.objects.create(text="Hello", status="PENDING")
        from predictions.views import PredictView
        view = PredictView()

        class DummyRequest:
            data = {"text": "Hello"}

        response = view.post(DummyRequest())
        self.assertEqual(response.status_code, 201)
        mock_channel.basic_publish.assert_called_once()

class PredictAPITests(TestCase):
    def setUp(self):
        self.client.defaults['CONTENT_TYPE'] = 'application/json'

    @patch("predictions.views.pika.BlockingConnection")
    def test_predict_post_creates_job(self, mock_connection):
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel
        response = self.client.post(
            reverse("predict"),
            data={"text": "test input"},             # pass dict here
            content_type="application/json"          # explicitly specify content type
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("job_id", response.json())

    def test_predict_status_returns_job(self):
        job = PredictionJob.objects.create(
            text="test", status="DONE", result="sample result"
        )
        response = self.client.get(
            reverse("predict-status", kwargs={"job_id": job.id})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "DONE")
        self.assertEqual(data["result"], "sample result")
