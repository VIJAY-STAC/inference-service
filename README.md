# Inference Service

A Django-based inference microservice with RabbitMQ message queue and Redis cache, containerized using Docker.

---

## Setup

1. **Clone the repository:**
   ```
   git clone https://github.com/VIJAY-STAC/inference-service.git
   cd inference_service
   
2. **Set up virtual environment & install dependencies:**
   ```bash
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   
3. **Run the whole app (API, worker, RabbitMQ, Redis) using Docker Compose**
    ```bash 
    docker-compose up --build

4. **run manually  Apply migrations**
    ```bash 
    python manage.py makemigrations
    python manage.py migrate

5. **Start Django API server**
    ```bash 
    python manage.py runserver 0.0.0.0:8000

6. **Start the worker in a separate terminal**
    ```bash 
    python3 worker.py
    
7. **API usage examples:**
    ```bash 
   curl --request POST \
      --url http://localhost:8000/predict/ \
      --header 'Content-Type: application/json' \
      --data '{
    	"text": "hello Ai"
    }'
    
8. **Check prediction job status:**
    ```bash 
    curl --request GET \
    --url http://localhost:8000/predict/fe462ea2-7e9c-4a90-be6f-694f259df903
    
9. **Notes**
   ```bash
   RabbitMQ Management UI is available at http://localhost:15672 (default user/pass: guest/guest).
   Redis runs on default port 6379.
   Worker listens to RabbitMQ queue prediction_queue.
   Redis used optionally as cache for results.





    
    
    