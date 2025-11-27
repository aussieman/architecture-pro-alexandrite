from fastapi import FastAPI
import requests
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = FastAPI()

# Настройка OpenTelemetry
trace.set_tracer_provider(
   TracerProvider(
       resource=Resource.create({"service.name": "service-b"})
   )
)

jaeger_exporter = OTLPSpanExporter(endpoint="http://simplest-collector:4318/v1/traces")
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Инструментация
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

tracer = trace.get_tracer(__name__)

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    with tracer.start_as_current_span("call_calculation_service"):
        response = requests.get(f"http://service-a:8080/calculate/{order_id}")
        calculation = response.json()
        return {"order_id": order_id, "status": "processed", "calculation": calculation}