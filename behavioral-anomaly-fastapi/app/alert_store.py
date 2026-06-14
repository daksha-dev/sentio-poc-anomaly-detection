from app.schemas import AlertOut


_alerts: list[AlertOut] = []


def store_alerts(alerts: list[AlertOut]) -> None:
    _alerts.extend(alerts)


def get_all_alerts() -> list[AlertOut]:
    return list(_alerts)


def get_alerts_for_student(student_id: str) -> list[AlertOut]:
    return [a for a in _alerts if a.student_id == student_id]


def reset() -> None:
    _alerts.clear()
