# ---------------------------------
# Imports
# ---------------------------------
import random
import time

from opentelemetry import trace
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# ---------------------------------
# Metrics (GLOBAL)
# ---------------------------------
WORKER_CHAOS_REQUESTS = Counter(
    "worker_chaos_requests_total",
    "Number of chaos mode requests in worker-service"
)

QUEUE_WAIT = Histogram("worker_queue_wait_seconds", "Simulated queue wait time")

resource = Resource.create({"service.name": "worker-service"})
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

# Manual tracer
tracer = trace.get_tracer("worker-service")

# ---------------------------------
# Routes
# ---------------------------------
@app.get("/work")
def work(chaos: bool = False):
    # --- Manual root span for worker service ---
    with tracer.start_as_current_span("worker.work") as span:
        span.set_attribute("chaos.enabled", chaos)

        if chaos:
            WORKER_CHAOS_REQUESTS.inc()

        # --- Chaos-mode slowdown ---
        if chaos and random.random() < 0.2:
            injected = 1.5
            span.set_attribute("latency.injected_ms", injected * 1000)
            time.sleep(injected)

        # --- Chaos-mode failure ---
        if chaos and random.random() < 0.1:
            error_msg = "Simulated worker failure"
            span.record_exception(Exception(error_msg))
            span.set_attribute("error", True)
            raise HTTPException(status_code=500, detail=error_msg)

        # --- Queue simulation ---
        queue_depth = random.randint(1, 10)
        span.set_attribute("queue.depth", queue_depth)

        queue_wait = queue_depth * random.uniform(0.05, 0.15)
        span.set_attribute("queue.wait_ms", queue_wait * 1000)

        QUEUE_WAIT.observe(queue_wait)
        time.sleep(queue_wait)

        return {"status": "ok", "chaos": chaos}
