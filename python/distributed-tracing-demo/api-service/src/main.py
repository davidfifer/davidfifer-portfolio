from fastapi import FastAPI
import requests
import random
import time

app = FastAPI()

@app.get("/process")
def process():
    time.sleep(random.uniform(0.1, 0.5))
    resp = requests.get("http://worker-service:8000/work")
    return {"worker_response": resp.json()}
