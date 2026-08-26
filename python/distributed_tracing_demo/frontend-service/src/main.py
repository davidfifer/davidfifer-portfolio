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
# Metrics (GLOBAL)
# ---------------------------------
FRONTEND_CHAOS_REQUESTS = Counter("frontend_chaos_requests_total",
    "Number of chaos mode requests in frontend-service"
)

resource = Resource.create({"service.name": "frontend-service"})
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

tracer = trace.get_tracer("frontend-service")

# ---------------------------------
# Routes
# ---------------------------------
@app.get("/start")
def start(chaos: bool = False):
    worker_url = "http://api-service:8000/process"

    # --- Root span for frontend service ---
    with tracer.start_as_current_span("frontend.start") as span:
        span.set_attribute("chaos.enabled", chaos)

        # --- Chaos-mode latency injection ---
        if chaos:
            FRONTEND_CHAOS_REQUESTS.inc()
            injected = random.uniform(0.1, 0.4)
            span.set_attribute("latency.injected_ms", injected * 1000)
            time.sleep(injected)

        try:
            # --- Child span for api call ---
            with tracer.start_as_current_span("frontend.call_api") as api_span:
                api_span.set_attribute("api.url", worker_url)
                api_span.set_attribute("chaos.enabled", chaos)

                resp = requests.get(worker_url, params={"chaos": chaos}                )
                resp.raise_for_status()

        except Exception as e:
            api_span.record_exception(e)
            api_span.set_attribute("error", True)
            raise HTTPException(status_code=500, detail=f"API error: {str(e)}")

        return {"api_response": resp.json(), "chaos": chaos}
