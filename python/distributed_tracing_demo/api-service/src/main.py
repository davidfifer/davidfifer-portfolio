# ---------------------------------
# Imports
# ---------------------------------
import requests
import random
import time

from opentelemetry import trace
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# ---------------------------------
# Constants
# ---------------------------------
MAX_RETRIES = 3
BASE_BACKOFF = 0.2  # seconds

# ---------------------------------
# Metrics (GLOBAL)
# ---------------------------------
API_CHAOS_REQUESTS = Counter(
    "api_chaos_requests_total",
    "Number of chaos mode requests in api-service"
)

RETRY_COUNT = Counter("worker_retry_total", "Total worker retries")

resource = Resource.create({"service.name": "api-service"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces"))
provider.add_span_processor(processor)
processor.force_flush()

# ---------------------------------
# Lifespan (startup/shutdown)
# ---------------------------------
@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    yield

# ---------------------------------
# Create the app WITH lifespan
# ---------------------------------
app = FastAPI(lifespan=lifespan)

# ---------------------------------
# Prometheus instrumentation
# MUST happen AFTER app is created,
# BEFORE the server starts.
# ---------------------------------
Instrumentator().instrument(app).expose(app)

FastAPIInstrumentor().instrument_app(app, tracer_provider=provider)
RequestsInstrumentor().instrument(tracer_provider=provider)

tracer = trace.get_tracer("api-service")

# ---------------------------------
# Routes
# ---------------------------------
@app.get("/process")
def process(chaos: bool = False):
    worker_url = "http://worker-service:8000/work"

    # --- Root span for api service ---
    with tracer.start_as_current_span("api.process") as span:
        span.set_attribute("chaos.enabled", chaos)

        # --- Chaos-mode latency injection ---
        if chaos:
            API_CHAOS_REQUESTS.inc()
            injected = random.uniform(0.1, 0.5)
            span.set_attribute("latency.injected_ms", injected * 1000)
            time.sleep(injected)

        # --- Retry loop for worker call ---
        for attempt in range(1, MAX_RETRIES + 1):
            with tracer.start_as_current_span("api.call_worker") as worker_span:
                worker_span.set_attribute("retry.attempt", attempt)
                worker_span.set_attribute("worker.url", worker_url)
                worker_span.set_attribute("chaos.enabled", chaos)

                try:
                    resp = requests.get(worker_url, params={"chaos": chaos})
                    resp.raise_for_status()

                    worker_span.set_attribute("retry.success", True)
                    return {"worker_response": resp.json(), "chaos": chaos}

                except Exception as e:
                    # Mark failure
                    worker_span.record_exception(e)
                    worker_span.set_attribute("retry.success", False)

                    # Increment Prometheus retry counter
                    RETRY_COUNT.inc()

                    # Backoff before next attempt
                    backoff = BASE_BACKOFF * attempt
                    worker_span.set_attribute("retry.backoff_ms", backoff * 1000)
                    time.sleep(backoff)

        # If we reach here, all retries failed
        raise HTTPException(status_code=500, detail="Worker failed after retries")
