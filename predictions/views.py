from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import PredictionJob
from .serializers import PredictionJobSerializer
import json
import pika  # RabbitMQ client
from django.core.cache import cache
import ssl

class PredictView(APIView):
    def post(self, request):
        print("api called")
        serializer = PredictionJobSerializer(data=request.data)
        if serializer.is_valid():
            job = serializer.save()

            # Send job to RabbitMQ queue
            try:
                # url = ""  # from CloudAMQP dashboard
                # params = pika.URLParameters(url)
                # # Disable certificate verification (development only!)
                # params.ssl_options = pika.SSLOptions(ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT), 'leopard.lmq.cloudamqp.com')
                # params.ssl_options.context.check_hostname = False
                # params.ssl_options.context.verify_mode = ssl.CERT_NONE
                params = pika.ConnectionParameters(host="rabbitmq")

                connection = pika.BlockingConnection(params)
            except Exception as e:
                print("exception is : ", e)
                return Response("connection not establish")

            channel = connection.channel()
            channel.queue_declare(queue='prediction_queue', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key='prediction_queue',
                body=json.dumps({"job_id": str(job.id), "text": job.text})
            )
            connection.close()

            # cache.set("my_key", "Hello Redis!", timeout=60)  # expires in 60 sec

            return Response({"job_id": str(job.id)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PredictStatusView(APIView):
    def get(self, request, job_id):
        job = get_object_or_404(PredictionJob, id=job_id)
        # value = cache.get("my_key")
        # print(value)  # Hello Redis!
        return Response({
            "status": job.status,
            "result": job.result
        })
