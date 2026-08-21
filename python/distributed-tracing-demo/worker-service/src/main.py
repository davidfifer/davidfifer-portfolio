from fastapi import FastAPI, HTTPException
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

# Manual tracer
tracer = trace.get_tracer("worker-service")


@app.get("/work")
def work(chaos: bool = False):

    # --- Manual root span for worker service ---
    with tracer.start_as_current_span("worker.work") as span:
        span.set_attribute("chaos.enabled", chaos)

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

        return {"status": "ok", "chaos": chaos}
