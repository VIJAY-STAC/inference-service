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

model_name = "openai-community/gpt2" # or "facebook/opt-iml-max-1.3b"
token = "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"
tokenizer = AutoTokenizer.from_pretrained(model_name, token=token if token else None)
model = AutoModelForCausalLM.from_pretrained(model_name, token=token if token else None)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def generate_answer(prompt: str) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        do_sample=True,
        temperature=0.7,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def callback(ch, method, properties, body):
    data = json.loads(body)
    job_id = data.get("job_id")
    text = data.get("text")    
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
    except Exception as e:
        job.status = "failed"
        job.result = str(e)

    job.save()
    ch.basic_ack(delivery_tag=method.delivery_tag)
        
params = pika.ConnectionParameters(host="rabbitmq")
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='prediction_queue', durable=True)
channel.basic_consume(queue='prediction_queue', on_message_callback=callback, auto_ack=False)
print("Consumer ready to consume Rabbitmq")
channel.start_consuming()
