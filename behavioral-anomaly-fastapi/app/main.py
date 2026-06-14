import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.schemas import BehaviorEvent, IngestResponse, HealthResponse, AlertOut
from app.detector import detect_anomalies
from app.alert_store import store_alerts, get_all_alerts, get_alerts_for_student, reset
from app.metrics import (
    total_events_processed, total_alerts_generated,
    high_risk_alerts_total, detection_latency_seconds,
    api_errors_total, metrics_response,
)
from app.logger import setup_logging, get_logger, log_request

setup_logging()
log = get_logger(__name__)

app = FastAPI(title="Behavioral Anomaly Detection API", version="1.0.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", response_model=HealthResponse)
async def health():
    t0 = time.perf_counter()
    latency = (time.perf_counter() - t0) * 1000
    log_request(log, "/health", latency)
    return HealthResponse(status="ok", service="behavioral-anomaly-fastapi")


@app.post("/ingest", response_model=IngestResponse)
async def ingest(events: list[BehaviorEvent]):
    t0 = time.perf_counter()
    try:
        total_events_processed.inc(len(events))

        with detection_latency_seconds.time():
            alerts = detect_anomalies(events)

        store_alerts(alerts)
        total_alerts_generated.inc(len(alerts))
        high_count = sum(1 for a in alerts if a.severity == "HIGH")
        high_risk_alerts_total.inc(high_count)

        from collections import Counter
        risk_summary = dict(Counter(a.severity for a in alerts))
        risk_summary.setdefault("LOW", 0)
        risk_summary.setdefault("MEDIUM", 0)
        risk_summary.setdefault("HIGH", 0)

        latency = (time.perf_counter() - t0) * 1000
        log_request(log, "/ingest", latency, len(events), len(alerts))

        return IngestResponse(
            processed_events=len(events),
            alerts_generated=len(alerts),
            risk_summary=risk_summary,
            alerts=alerts,
        )
    except Exception as e:
        api_errors_total.inc()
        latency = (time.perf_counter() - t0) * 1000
        log_request(log, "/ingest", latency, error=str(e))
        raise


@app.get("/alerts")
async def list_alerts():
    t0 = time.perf_counter()
    alerts = get_all_alerts()
    latency = (time.perf_counter() - t0) * 1000
    log_request(log, "/alerts", latency)
    return alerts


@app.get("/alerts/{student_id}")
async def student_alerts(student_id: str):
    t0 = time.perf_counter()
    alerts = get_alerts_for_student(student_id)
    latency = (time.perf_counter() - t0) * 1000
    log_request(log, f"/alerts/{student_id}", latency)
    return alerts


@app.post("/reset")
async def reset_alerts():
    t0 = time.perf_counter()
    reset()
    latency = (time.perf_counter() - t0) * 1000
    log_request(log, "/reset", latency)
    return {"status": "ok", "message": "All alerts cleared"}


@app.get("/metrics")
async def metrics():
    return metrics_response()
