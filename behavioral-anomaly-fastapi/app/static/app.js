const SAMPLE_EVENTS = [
  {
    "student_id": "S001",
    "timestamp": "2026-06-13T10:00:00",
    "activity_type": "login",
    "duration_minutes": 5,
    "sentiment_score": -0.7,
    "missed_classes": 3,
    "assignment_delay_days": 5,
    "social_interaction_score": 0.2
  },
  {
    "student_id": "S002",
    "timestamp": "2026-06-13T10:05:00",
    "activity_type": "login",
    "duration_minutes": 45,
    "sentiment_score": 0.6,
    "missed_classes": 0,
    "assignment_delay_days": 0,
    "social_interaction_score": 0.85
  },
  {
    "student_id": "S003",
    "timestamp": "2026-06-13T10:10:00",
    "activity_type": "login",
    "duration_minutes": 8,
    "sentiment_score": -0.5,
    "missed_classes": 1,
    "assignment_delay_days": 2,
    "social_interaction_score": 0.5
  },
  {
    "student_id": "S004",
    "timestamp": "2026-06-13T10:15:00",
    "activity_type": "login",
    "duration_minutes": 3,
    "sentiment_score": -0.8,
    "missed_classes": 4,
    "assignment_delay_days": 6,
    "social_interaction_score": 0.15
  },
  {
    "student_id": "S005",
    "timestamp": "2026-06-13T10:20:00",
    "activity_type": "login",
    "duration_minutes": 12,
    "sentiment_score": 0.3,
    "missed_classes": 5,
    "assignment_delay_days": 4,
    "social_interaction_score": 0.4
  }
];

const textarea = document.getElementById("eventInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const sampleBtn = document.getElementById("sampleBtn");
const resetBtn = document.getElementById("resetBtn");
const errorMsg = document.getElementById("errorMsg");
const loading = document.getElementById("loading");
const summaryCards = document.getElementById("summaryCards");
const alertsContainer = document.getElementById("alertsContainer");
const alertCards = document.getElementById("alertCards");

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.add("visible");
}

function hideError() {
  errorMsg.textContent = "";
  errorMsg.classList.remove("visible");
}

function showLoading() {
  loading.classList.remove("hidden");
  summaryCards.classList.add("hidden");
  alertsContainer.classList.add("hidden");
}

function hideLoading() {
  loading.classList.add("hidden");
}

function renderResults(data) {
  summaryCards.classList.remove("hidden");
  alertsContainer.classList.remove("hidden");

  document.getElementById("eventsProcessed").textContent = data.processed_events;
  document.getElementById("alertsGenerated").textContent = data.alerts_generated;
  document.getElementById("highRiskCount").textContent = data.risk_summary.HIGH || 0;

  alertCards.innerHTML = "";
  if (!data.alerts || data.alerts.length === 0) {
    alertCards.innerHTML = '<p style="color:#888;padding:12px 0">No alerts detected.</p>';
    return;
  }

  data.alerts.forEach(a => {
    const div = document.createElement("div");
    div.className = `alert-card severity-${a.severity}`;
    div.innerHTML = `
      <div class="alert-header">
        <span class="student-name">${a.student_id}</span>
        <span class="badge badge-${a.severity}">${a.severity}</span>
        <span class="badge-pattern">${a.pattern}</span>
      </div>
      <p class="alert-desc">${a.description}</p>
      <div class="alert-meta">
        <span>Confidence: ${(a.confidence * 100).toFixed(0)}%</span>
        <span>ID: ${a.alert_id}</span>
      </div>
    `;
    alertCards.appendChild(div);
  });
}

analyzeBtn.addEventListener("click", async () => {
  hideError();
  const raw = textarea.value.trim();
  if (!raw) {
    showError("Please paste JSON event data.");
    return;
  }

  let events;
  try {
    events = JSON.parse(raw);
  } catch {
    showError("Invalid JSON format.");
    return;
  }

  if (!Array.isArray(events)) {
    showError("Expected a JSON array of events.");
    return;
  }

  showLoading();
  try {
    const res = await fetch("/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(events),
    });
    if (!res.ok) {
      const err = await res.json();
      showError(err.detail || "Request failed.");
      hideLoading();
      return;
    }
    const data = await res.json();
    hideLoading();
    renderResults(data);
  } catch (e) {
    hideLoading();
    showError("Network error: " + e.message);
  }
});

sampleBtn.addEventListener("click", () => {
  hideError();
  textarea.value = JSON.stringify(SAMPLE_EVENTS, null, 2);
});

resetBtn.addEventListener("click", async () => {
  hideError();
  try {
    await fetch("/reset", { method: "POST" });
    summaryCards.classList.add("hidden");
    alertsContainer.classList.add("hidden");
    textarea.value = "";
  } catch (e) {
    showError("Reset failed: " + e.message);
  }
});
