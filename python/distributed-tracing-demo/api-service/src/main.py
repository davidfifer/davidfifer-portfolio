from fastapi import FastAPI, HTTPException
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

tracer = trace.get_tracer("api-service")


@app.get("/process")
def process(chaos: bool = False):

    # --- Root span for api service ---
    with tracer.start_as_current_span("api.process") as span:
        span.set_attribute("chaos.enabled", chaos)

        # --- Chaos-mode latency injection ---
        if chaos:
            injected = random.uniform(0.1, 0.5)
            span.set_attribute("latency.injected_ms", injected * 1000)
            time.sleep(injected)

        try:
            # --- Child span for worker call ---
            with tracer.start_as_current_span("api.call_worker") as worker_span:
                worker_span.set_attribute("worker.url", "http://worker-service:8000/work")
                worker_span.set_attribute("chaos.enabled", chaos)

                resp = requests.get(
                    "http://worker-service:8000/work",
                    params={"chaos": chaos}
                )
                resp.raise_for_status()

        except Exception as e:
            worker_span.record_exception(e)
            worker_span.set_attribute("error", True)
            raise HTTPException(status_code=500, detail=f"Worker error: {str(e)}")

        return {"worker_response": resp.json(), "chaos": chaos}
