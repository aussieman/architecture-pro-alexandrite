from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()

# Настройка OpenTelemetry
trace.set_tracer_provider(
   TracerProvider(
       resource=Resource.create({"service.name": "service-a"})
   )
)

jaeger_exporter = OTLPSpanExporter(endpoint="http://simplest-collector:4318/v1/traces")
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Инструментация
FastAPIInstrumentor.instrument_app(app)

@app.get("/calculate/{order_id}")
async def calculate(order_id: int):
    # Простой расчет стоимости
    cost = order_id * 100
    return {"order_id": order_id, "calculated_cost": cost}