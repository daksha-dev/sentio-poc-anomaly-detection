import uuid
from datetime import datetime
from app.schemas import BehaviorEvent, AlertOut


THRESHOLDS = {
    "missed_classes": 3,
    "sentiment_score": -0.6,
    "assignment_delay_days": 4,
    "social_interaction_score": 0.3,
    "duration_minutes": 5,
}


def detect_anomalies(events: list[BehaviorEvent]) -> list[AlertOut]:
    alerts: list[AlertOut] = []

    for event in events:
        student_alerts = _analyze_event(event)
        alerts.extend(student_alerts)

        multi_risk = _check_multi_signal(alerts, event.student_id)
        if multi_risk:
            alerts.append(multi_risk)

    return alerts


def _make_alert(event: BehaviorEvent, pattern: str, severity: str,
                confidence: float, description: str, evidence: dict) -> AlertOut:
    return AlertOut(
        alert_id=str(uuid.uuid4())[:8],
        timestamp=event.timestamp.isoformat() if isinstance(event.timestamp, datetime) else event.timestamp,
        student_id=event.student_id,
        severity=severity,
        pattern=pattern,
        confidence=round(confidence, 2),
        description=description,
        evidence=evidence,
    )


def _analyze_event(event: BehaviorEvent) -> list[AlertOut]:
    alerts: list[AlertOut] = []

    if event.missed_classes is not None and event.missed_classes >= THRESHOLDS["missed_classes"]:
        conf = min(0.95, 0.5 + event.missed_classes * 0.1)
        alerts.append(_make_alert(
            event, "CHRONIC_ABSENCE", "HIGH",
            conf,
            f"Student missed {event.missed_classes} classes.",
            {"missed_classes": event.missed_classes},
        ))

    if event.sentiment_score is not None and event.sentiment_score <= THRESHOLDS["sentiment_score"]:
        conf = min(0.9, 0.5 + abs(event.sentiment_score) * 0.5)
        alerts.append(_make_alert(
            event, "NEGATIVE_SENTIMENT", "HIGH",
            conf,
            f"Sentiment score critically low at {event.sentiment_score}.",
            {"sentiment_score": event.sentiment_score},
        ))

    if event.assignment_delay_days is not None and event.assignment_delay_days >= THRESHOLDS["assignment_delay_days"]:
        conf = min(0.9, 0.5 + event.assignment_delay_days * 0.08)
        alerts.append(_make_alert(
            event, "LATE_SUBMISSIONS", "MEDIUM",
            conf,
            f"Assignments delayed by {event.assignment_delay_days} days.",
            {"assignment_delay_days": event.assignment_delay_days},
        ))

    if event.social_interaction_score is not None and event.social_interaction_score <= THRESHOLDS["social_interaction_score"]:
        conf = min(0.85, 0.4 + (1.0 - event.social_interaction_score) * 0.5)
        alerts.append(_make_alert(
            event, "SOCIAL_ISOLATION", "MEDIUM",
            conf,
            f"Social interaction score very low at {event.social_interaction_score}.",
            {"social_interaction_score": event.social_interaction_score},
        ))

    if event.duration_minutes is not None and event.duration_minutes <= THRESHOLDS["duration_minutes"]:
        conf = 0.6 + (1.0 - event.duration_minutes / THRESHOLDS["duration_minutes"]) * 0.2
        conf = min(0.8, conf)
        alerts.append(_make_alert(
            event, "LOW_ENGAGEMENT", "MEDIUM",
            conf,
            f"Session duration only {event.duration_minutes} minutes.",
            {"duration_minutes": event.duration_minutes},
        ))

    if event.missed_classes is not None and event.assignment_delay_days is not None:
        if event.missed_classes >= 2 and event.assignment_delay_days >= 3:
            conf = min(0.95, 0.6 + event.missed_classes * 0.05 + event.assignment_delay_days * 0.05)
            alerts.append(_make_alert(
                event, "ACADEMIC_WITHDRAWAL", "HIGH",
                conf,
                "Multiple academic disengagement signals detected.",
                {
                    "missed_classes": event.missed_classes,
                    "assignment_delay_days": event.assignment_delay_days,
                },
            ))

    return alerts


def _check_multi_signal(alerts: list[AlertOut], student_id: str) -> AlertOut | None:
    student_alerts = [a for a in alerts if a.student_id == student_id]
    medium_plus = [a for a in student_alerts if a.severity in ("MEDIUM", "HIGH")]
    if len(medium_plus) >= 3 and not any(a.pattern == "MULTI_SIGNAL_RISK" for a in student_alerts):
        return AlertOut(
            alert_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            student_id=student_id,
            severity="HIGH",
            pattern="MULTI_SIGNAL_RISK",
            confidence=round(min(0.95, 0.6 + len(medium_plus) * 0.1), 2),
            description=f"Student flagged for {len(medium_plus)} distinct risk patterns.",
            evidence={"patterns": list(set(a.pattern for a in medium_plus))},
        )
    return None
