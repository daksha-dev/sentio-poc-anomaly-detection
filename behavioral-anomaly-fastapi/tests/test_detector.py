import pytest
from datetime import datetime
from app.schemas import BehaviorEvent
from app.detector import detect_anomalies


def make_event(student_id="S001", **overrides):
    defaults = {
        "student_id": student_id,
        "timestamp": datetime(2026, 6, 13, 10, 0, 0),
        "activity_type": "login",
        "duration_minutes": 45,
        "sentiment_score": 0.5,
        "missed_classes": 0,
        "assignment_delay_days": 0,
        "social_interaction_score": 0.8,
    }
    defaults.update(overrides)
    return BehaviorEvent(**defaults)


def test_normal_student_no_alerts():
    events = [make_event("S_NORMAL")]
    alerts = detect_anomalies(events)
    assert len(alerts) == 0


def test_high_missed_classes_triggers_chronic_absence():
    events = [make_event(missed_classes=5)]
    alerts = detect_anomalies(events)
    patterns = [a.pattern for a in alerts]
    assert "CHRONIC_ABSENCE" in patterns


def test_negative_sentiment_triggers_alert():
    events = [make_event(sentiment_score=-0.8)]
    alerts = detect_anomalies(events)
    patterns = [a.pattern for a in alerts]
    assert "NEGATIVE_SENTIMENT" in patterns


def test_high_assignment_delay_triggers_late_submissions():
    events = [make_event(assignment_delay_days=6)]
    alerts = detect_anomalies(events)
    patterns = [a.pattern for a in alerts]
    assert "LATE_SUBMISSIONS" in patterns


def test_low_social_interaction_triggers_isolation():
    events = [make_event(social_interaction_score=0.15)]
    alerts = detect_anomalies(events)
    patterns = [a.pattern for a in alerts]
    assert "SOCIAL_ISOLATION" in patterns


def test_low_engagement_triggers_alert():
    events = [make_event(duration_minutes=3)]
    alerts = detect_anomalies(events)
    patterns = [a.pattern for a in alerts]
    assert "LOW_ENGAGEMENT" in patterns


def test_academic_withdrawal_combined():
    events = [make_event(missed_classes=3, assignment_delay_days=5)]
    alerts = detect_anomalies(events)
    patterns = [a.pattern for a in alerts]
    assert "ACADEMIC_WITHDRAWAL" in patterns


def test_multi_signal_high_risk():
    events = [make_event(
        missed_classes=3,
        sentiment_score=-0.7,
        assignment_delay_days=5,
        social_interaction_score=0.2,
        duration_minutes=3,
    )]
    alerts = detect_anomalies(events)
    patterns = [a.pattern for a in alerts]
    assert "MULTI_SIGNAL_RISK" in patterns
    multi = [a for a in alerts if a.pattern == "MULTI_SIGNAL_RISK"][0]
    assert multi.severity == "HIGH"
    assert multi.confidence > 0.5


def test_alert_has_required_fields():
    events = [make_event(missed_classes=5)]
    alerts = detect_anomalies(events)
    alert = alerts[0]
    assert alert.alert_id
    assert alert.timestamp
    assert alert.student_id == "S001"
    assert alert.severity in ("LOW", "MEDIUM", "HIGH")
    assert alert.pattern
    assert 0 < alert.confidence <= 1.0
    assert alert.description
    assert isinstance(alert.evidence, dict)
