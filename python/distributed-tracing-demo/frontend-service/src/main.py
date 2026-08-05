from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/start")
def start():
    resp = requests.get("http://api-service:8000/process")
    return {"api_response": resp.json()}
