from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BehaviorEvent(BaseModel):
    student_id: str = Field(..., examples=["S001"])
    timestamp: datetime = Field(..., examples=["2026-06-13T10:00:00"])
    activity_type: str = Field(..., examples=["login"])
    duration_minutes: Optional[float] = Field(default=None, examples=[5])
    sentiment_score: Optional[float] = Field(default=None, examples=[-0.7])
    missed_classes: Optional[int] = Field(default=None, examples=[3])
    assignment_delay_days: Optional[int] = Field(default=None, examples=[5])
    social_interaction_score: Optional[float] = Field(default=None, examples=[0.2])


class AlertOut(BaseModel):
    alert_id: str
    timestamp: str
    student_id: str
    severity: str
    pattern: str
    confidence: float
    description: str
    evidence: dict


class IngestResponse(BaseModel):
    processed_events: int
    alerts_generated: int
    risk_summary: dict
    alerts: list[AlertOut]


class HealthResponse(BaseModel):
    status: str
    service: str
