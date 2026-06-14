# Behavioral Anomaly Detection FastAPI Service

A production-style FastAPI ML service that detects student behavioral distress and anomaly patterns from event logs. Accepts JSON behavioral data, runs rule-based risk scoring, returns structured alerts, exposes Prometheus metrics, and provides a simple dashboard.

---

## Problem Statement

Educational institutions collect vast amounts of behavioral data — login frequency, sentiment scores, assignment timelines, class attendance, social engagement — but rarely act on it proactively. A student can be in distress for days without anyone noticing until a crisis emerges.

This service provides that proactive alert layer: ingest behavioral event logs, detect distress patterns in real time, and surface actionable alerts before situations escalate.

**Important:** This is a **prototype using synthetic/sample data** and rule-based scoring. It is not a clinical diagnostic system and should not be used for medical or psychological diagnosis.

---

## Why Behavioral Anomaly Detection Matters

- Early intervention reduces student dropout rates by up to 30% (education research)
- Counselors can't manually monitor hundreds of students daily
- Pattern-based detection catches subtle signals that humans miss
- Alerts create a documented trail for follow-up and escalation

---

## Architecture Flow

```
JSON Events → Pydantic Validation → Rule Engine → Alert Scoring → API Response → Dashboard → Prometheus Metrics
                                          ↓
                                   In-Memory Alert Store
                                          ↓
                                   Structured JSON Logging
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI 0.115 |
| Validation | Pydantic v2 |
| Detection | Rule-based scoring (extensible to scikit-learn) |
| Metrics | prometheus-client |
| Logging | Structured JSON to stdout |
| Testing | pytest + httpx |
| Container | Docker + docker-compose |
| CI/CD | GitHub Actions |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Dashboard UI |
| GET | `/health` | Health check |
| POST | `/ingest` | Accept JSON list of behavior events, run detection, return alerts |
| GET | `/alerts` | List all stored alerts |
| GET | `/alerts/{student_id}` | Get alerts for a specific student |
| POST | `/reset` | Clear all stored alerts |
| GET | `/metrics` | Prometheus metrics endpoint |

---

## Detection Patterns

| Pattern | Trigger | Severity |
|---|---|---|
| LOW_ENGAGEMENT | Session duration ≤ 5 min | MEDIUM |
| NEGATIVE_SENTIMENT | Sentiment score ≤ -0.6 | HIGH |
| ACADEMIC_WITHDRAWAL | Missed classes ≥ 2 AND assignment delay ≥ 3 days | HIGH |
| CHRONIC_ABSENCE | Missed classes ≥ 3 | HIGH |
| SOCIAL_ISOLATION | Social interaction ≤ 0.3 | MEDIUM |
| LATE_SUBMISSIONS | Assignment delay ≥ 4 days | MEDIUM |
| MULTI_SIGNAL_RISK | 3+ MEDIUM/HIGH patterns on one student | HIGH |

---

## Sample Input/Output

**Input** (`POST /ingest`):

```json
[
  {
    "student_id": "S001",
    "timestamp": "2026-06-13T10:00:00",
    "activity_type": "login",
    "duration_minutes": 5,
    "sentiment_score": -0.7,
    "missed_classes": 3,
    "assignment_delay_days": 5,
    "social_interaction_score": 0.2
  }
]
```

**Output**:

```json
{
  "processed_events": 1,
  "alerts_generated": 6,
  "risk_summary": {
    "LOW": 0,
    "MEDIUM": 3,
    "HIGH": 3
  },
  "alerts": [
    {
      "alert_id": "a1b2c3d4",
      "timestamp": "2026-06-13T10:00:00",
      "student_id": "S001",
      "severity": "HIGH",
      "pattern": "CHRONIC_ABSENCE",
      "confidence": 0.85,
      "description": "Student missed 3 classes.",
      "evidence": {"missed_classes": 3}
    }
  ]
}
```

---

## Local Setup

```bash
cd behavioral-anomaly-fastapi

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload

# Open browser
# Dashboard:  http://localhost:8000
# API Docs:   http://localhost:8000/docs
# Metrics:    http://localhost:8000/metrics
```

---

## Docker Setup

```bash
docker compose up --build
# Service available at http://localhost:8000
```

---

## Testing

```bash
pytest -v
```

Tests cover:
- `/health` returns 200 with correct payload
- `/alerts` returns list
- `/ingest` accepts valid event JSON and returns alerts
- `/ingest` rejects invalid JSON (Pydantic validation)
- Detector catches high-risk multi-signal cases
- Detector validates all 7 patterns independently
- `/reset` clears all stored alerts
- `/metrics` serves Prometheus format

---

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`):

- **On push/PR to main:** Checkout code, set up Python 3.11, install dependencies, run pytest
- **Docker build job:** Verifies Docker image builds successfully

---

## Observability

- **Prometheus metrics** at `/metrics`: `total_events_processed`, `total_alerts_generated`, `high_risk_alerts_total`, `detection_latency_seconds`, `api_errors_total`
- **Structured JSON logs** to stdout with: `request_id`, `endpoint`, `latency_ms`, `events_processed`, `alerts_generated`, `error`
- **FastAPI built-in OpenAPI docs** at `/docs` and `/redoc`

---

## Project Structure

```
behavioral-anomaly-fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application, all endpoints
│   ├── schemas.py           # Pydantic models
│   ├── detector.py          # Rule-based anomaly detection engine
│   ├── alert_store.py       # In-memory alert storage
│   ├── metrics.py           # Prometheus metrics
│   ├── logger.py            # Structured JSON logging
│   ├── sample_data.py       # Demo JSON events
│   ├── static/
│   │   ├── styles.css
│   │   └── app.js
│   └── templates/
│       └── index.html
├── tests/
│   ├── __init__.py
│   ├── test_api.py          # API integration tests
│   └── test_detector.py     # Unit tests for detection logic
├── data/
│   └── sample_events.json   # Sample event payload
├── .github/workflows/ci.yml
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Limitations

- **Rule-based prototype:** Detection uses threshold-based rules, not trained ML models. Confidence scores are heuristic, not statistical.
- **Synthetic data:** Sample data is hand-crafted, not real student records. Real-world distributions will differ.
- **In-memory storage:** Alerts are stored in memory and lost on restart. No persistence layer.
- **Not a diagnostic system:** This is a screening/alerting tool, not a clinical or psychological assessment. Human judgment is always required.

---

## Future Upgrades

- **Isolation Forest:** Replace/extend rule engine with unsupervised anomaly detection
- **River/ADWIN drift detection:** Online learning that adapts to changing baselines over time
- **PostgreSQL storage:** Persistent alert history with student profiles
- **JWT auth:** Secure counselor access with role-based permissions
- **Grafana dashboard:** Visual dashboards on top of Prometheus metrics
- **Notification system:** Email/Slack/webhook alerts for high-risk cases
- **Counsellor workflow integration:** Acknowledge/resolve/comment on alerts with audit trail

---

## Resume Bullet

> Built a Dockerized FastAPI behavioral anomaly detection service with Pydantic validation, rule-based risk scoring for 7 distress patterns, Prometheus metrics, structured JSON logging, pytest API tests, and GitHub Actions CI/CD.

---

## Interview Demo Script

```bash
# 1. Start the service
uvicorn app.main:app --reload

# 2. Health check
curl http://localhost:8000/health

# 3. Ingest sample data
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d @data/sample_events.json

# 4. List all alerts
curl http://localhost:8000/alerts

# 5. Filter by student
curl http://localhost:8000/alerts/S001

# 6. Check metrics
curl http://localhost:8000/metrics

# 7. Open dashboard
# Browser → http://localhost:8000

# 8. Show API docs
# Browser → http://localhost:8000/docs

# 9. Reset and verify
curl -X POST http://localhost:8000/reset
curl http://localhost:8000/alerts

# 10. Run tests
pytest -v
```

---

## Screenshots to Capture

1. **Dashboard home page** with sample data loaded
2. **Dashboard results view** showing summary cards and alert cards with severity badges
3. **Swagger docs** (`/docs`) showing all 6 endpoints
4. **Health endpoint JSON response**
5. **Ingest endpoint response** showing structured alert output
6. **Metrics endpoint** showing Prometheus counters
7. **Terminal JSON logs** from uvicorn output
8. **pytest output** with all tests passing
9. **Docker build output** showing successful image build
