from fastapi import FastAPI
import requests
import random
import time

# --- OpenTelemetry Setup ---
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

resource = Resource.create({"service.name": "api-service"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces"))
provider.add_span_processor(processor)
processor.force_flush()

app = FastAPI()

FastAPIInstrumentor().instrument_app(app, tracer_provider=provider)
RequestsInstrumentor().instrument(tracer_provider=provider)

@app.get("/process")
def process():
    time.sleep(random.uniform(0.1, 0.5))
    resp = requests.get("http://worker-service:8000/work")
    return {"worker_response": resp.json()}
