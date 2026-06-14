from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response


total_events_processed = Counter(
    "total_events_processed",
    "Total number of behavioral events processed",
)

total_alerts_generated = Counter(
    "total_alerts_generated",
    "Total number of alerts generated",
)

high_risk_alerts_total = Counter(
    "high_risk_alerts_total",
    "Total HIGH severity alerts generated",
)

detection_latency_seconds = Histogram(
    "detection_latency_seconds",
    "Latency of anomaly detection in seconds",
)

api_errors_total = Counter(
    "api_errors_total",
    "Total number of API errors",
)


def metrics_response() -> Response:
    return Response(content=generate_latest(), media_type="text/plain")
