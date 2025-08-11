import os
import json
import pika
import django
import ssl
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inference_service.settings")
django.setup()

from predictions.models import PredictionJob

print("model code start here ....")
model_name = "openai-community/gpt2"
# or use: model_name = "facebook/opt-iml-max-1.3b"
token = "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"

# Load tokenizer and model with authentication if token is set
print("model code start here  ####....")
tokenizer = AutoTokenizer.from_pretrained(model_name, token=token if token else None)
print("model code start here  ******")
model = AutoModelForCausalLM.from_pretrained(model_name, token=token if token else None)
print("model found ******")

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def generate_answer(prompt: str) -> str:
    # Tokenize input and move tensors to model device
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    # Generate output tokens with sampling and temperature
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        do_sample=True,
        temperature=0.7,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# ---- RabbitMQ callback ----
def callback(ch, method, properties, body):
    print("task picked")
    data = json.loads(body)
    job_id = data.get("job_id")
    text = data.get("text")

    jobs = PredictionJob.objects.all().count()
    
    try:
        job = PredictionJob.objects.get(id=job_id)
    except PredictionJob.DoesNotExist:
        print(f"Job {job_id} not found!")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    try:
        result = generate_answer(text)
        job.status = "done"
        job.result = result
        print("result found.")
    except Exception as e:
        job.status = "failed"
        job.result = str(e)
        print("result not found.")

    job.save()
    ch.basic_ack(delivery_tag=method.delivery_tag)
        


url = "amqps://ehfuciuh:UZMuO4Pdb7x2DweqtZusuAfubexEC_TS@leopard.lmq.cloudamqp.com/ehfuciuh"  
params = pika.URLParameters(url)
# Disable certificate verification (development only!)
params.ssl_options = pika.SSLOptions(ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT), 'leopard.lmq.cloudamqp.com')
params.ssl_options.context.check_hostname = False
params.ssl_options.context.verify_mode = ssl.CERT_NONE
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='prediction_queue', durable=True)
# channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='prediction_queue', on_message_callback=callback, auto_ack=False)
print("Consumer ready to consume Rabbitmq")
channel.start_consuming()
