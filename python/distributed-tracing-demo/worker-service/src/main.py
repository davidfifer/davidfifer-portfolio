from fastapi import FastAPI
import random
import time

app = FastAPI()

@app.get("/work")
def work():
    if random.random() < 0.2:
        time.sleep(1.5)
    if random.random() < 0.1:
        raise Exception("Simulated worker failure")
    return {"status": "ok"}
