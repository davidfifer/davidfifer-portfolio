from fastapi import FastAPI
import random
import time

# --- OpenTelemetry Setup ---
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

resource = Resource.create({"service.name": "worker-service"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces"))
provider.add_span_processor(processor)
processor.force_flush()

app = FastAPI()

FastAPIInstrumentor().instrument_app(app, tracer_provider=provider)

@app.get("/work")
def work():
    if random.random() < 0.2:
        time.sleep(1.5)
    if random.random() < 0.1:
        raise Exception("Simulated worker failure")
    return {"status": "ok"}
