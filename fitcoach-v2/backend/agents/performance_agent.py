"""
Agent Performance — Suivi, analyse et visualisation des progrès.
"""
import json
from datetime import datetime, timedelta, timezone
from shared.db import get_table, now_iso
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def record_session(user_id: str, params: dict) -> dict:
    """Record a completed training session."""
    table = get_table("sessions")
    perf_table = get_table("performance")

    session_id = params.get("sessionId", now_iso())
    exercises = params.get("exercises", [])
    duration_minutes = params.get("durationMinutes", 0)
    avg_score = params.get("avgPostureScore", 0)

    # Save session
    table.put_item(Item={
        "userId": user_id,
        "sessionId": session_id,
        "exercises": json.dumps(exercises, ensure_ascii=False),
        "durationMinutes": duration_minutes,
        "avgPostureScore": Decimal(str(avg_score)),
        "totalReps": sum(e.get("reps", 0) * e.get("sets", 1) for e in exercises),
        "totalSets": sum(e.get("sets", 0) for e in exercises),
        "createdAt": now_iso(),
    })

    # Update per-exercise performance
    today = datetime.now(timezone.utc).date().isoformat()
    for exercise in exercises:
        ex_name = exercise.get("name", "unknown")
        perf_table.put_item(Item={
            "userId": user_id,
            "exerciseDate": f"{ex_name}#{today}",
            "exercise": ex_name,
            "date": today,
            "reps": exercise.get("reps", 0),
            "sets": exercise.get("sets", 0),
            "score": Decimal(str(exercise.get("score", 0))),
            "volume": exercise.get("reps", 0) * exercise.get("sets", 1),
        })

    # Calculate XP
    xp_earned = 100  # Base XP for completing a session
    if avg_score > 80:
        xp_earned += 50
    if avg_score > 95:
        xp_earned += 100

    return {
        "message": "Séance enregistrée",
        "sessionId": session_id,
        "totalReps": sum(e.get("reps", 0) * e.get("sets", 1) for e in exercises),
        "avgScore": avg_score,
        "xpEarned": xp_earned,
    }


def get_stats(user_id: str, params: dict) -> dict:
    """Get global performance statistics."""
    table = get_table("sessions")

    # Query last 30 days of sessions
    response = table.query(
        KeyConditionExpression="userId = :uid",
        ExpressionAttributeValues={":uid": user_id},
        ScanIndexForward=False,
        Limit=30,
    )

    sessions = response.get("Items", [])

    if not sessions:
        return {
            "totalSessions": 0,
            "totalReps": 0,
            "avgScore": 0,
            "streak": 0,
            "message": "Aucune séance enregistrée. Commencez votre premier entraînement !",
        }

    total_reps = sum(int(s.get("totalReps", 0)) for s in sessions)
    total_sets = sum(int(s.get("totalSets", 0)) for s in sessions)
    avg_score = sum(float(s.get("avgPostureScore", 0)) for s in sessions) / len(sessions)
    total_duration = sum(int(s.get("durationMinutes", 0)) for s in sessions)

    return {
        "totalSessions": len(sessions),
        "totalReps": total_reps,
        "totalSets": total_sets,
        "avgPostureScore": round(avg_score, 1),
        "totalDurationMinutes": total_duration,
        "last30Days": True,
    }


def get_history(user_id: str, params: dict) -> dict:
    """Get session history."""
    table = get_table("sessions")
    limit = params.get("limit", 10)

    response = table.query(
        KeyConditionExpression="userId = :uid",
        ExpressionAttributeValues={":uid": user_id},
        ScanIndexForward=False,
        Limit=limit,
    )

    sessions = []
    for item in response.get("Items", []):
        sessions.append({
            "sessionId": item["sessionId"],
            "date": item.get("createdAt", ""),
            "totalReps": int(item.get("totalReps", 0)),
            "totalSets": int(item.get("totalSets", 0)),
            "avgScore": float(item.get("avgPostureScore", 0)),
            "durationMinutes": int(item.get("durationMinutes", 0)),
        })

    return {"history": sessions}


def get_personal_records(user_id: str, params: dict) -> dict:
    """Get personal records per exercise."""
    perf_table = get_table("performance")

    response = perf_table.query(
        KeyConditionExpression="userId = :uid",
        ExpressionAttributeValues={":uid": user_id},
    )

    # Aggregate PRs
    prs = {}
    for item in response.get("Items", []):
        exercise = item.get("exercise", "")
        volume = int(item.get("volume", 0))
        score = float(item.get("score", 0))

        if exercise not in prs:
            prs[exercise] = {"maxVolume": 0, "maxScore": 0, "date": ""}

        if volume > prs[exercise]["maxVolume"]:
            prs[exercise]["maxVolume"] = volume
            prs[exercise]["date"] = item.get("date", "")

        if score > prs[exercise]["maxScore"]:
            prs[exercise]["maxScore"] = score

    return {"personalRecords": prs}


def handle(user_id: str, intent: str, params: dict) -> dict:
    """Agent Performance entry point."""
    if intent in ("record", "enregistrer", "save"):
        return record_session(user_id, params)
    elif intent in ("stats", "statistiques", "résumé"):
        return get_stats(user_id, params)
    elif intent in ("history", "historique"):
        return get_history(user_id, params)
    elif intent in ("pr", "records", "personal records"):
        return get_personal_records(user_id, params)
    else:
        return get_stats(user_id, params)
