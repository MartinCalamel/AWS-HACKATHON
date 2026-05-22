"""
Agent Repos — Gestion de la récupération et prévention du surentraînement.
"""
import json
from datetime import datetime, timedelta, timezone
from shared.db import get_table


# Rest time recommendations (seconds) by goal
REST_TIMES = {
    "endurance": {"min": 30, "max": 60, "default": 45},
    "hypertrophy": {"min": 60, "max": 90, "default": 75},
    "strength": {"min": 120, "max": 180, "default": 150},
    "general": {"min": 60, "max": 90, "default": 60},
}

# Maximum weekly volume thresholds by level
MAX_WEEKLY_VOLUME = {
    "beginner": 300,
    "intermediate": 600,
    "advanced": 1000,
}


def get_rest_time(user_id: str, params: dict) -> dict:
    """Calculate recommended rest time between sets."""
    exercise = params.get("exercise", "")
    goal = params.get("goal", "general")
    current_set = params.get("currentSet", 1)
    total_sets = params.get("totalSets", 3)
    fatigue_level = params.get("fatigueLevel", 0.5)

    base = REST_TIMES.get(goal, REST_TIMES["general"])
    recommended = base["default"]

    # Increase rest as fatigue builds
    fatigue_multiplier = 1 + (fatigue_level * 0.5)
    # Increase rest for later sets
    set_multiplier = 1 + ((current_set - 1) / total_sets) * 0.3

    recommended = int(recommended * fatigue_multiplier * set_multiplier)
    recommended = max(base["min"], min(recommended, base["max"] + 30))

    return {
        "restSeconds": recommended,
        "exercise": exercise,
        "goal": goal,
        "currentSet": current_set,
        "fatigueLevel": round(fatigue_level, 2),
        "message": f"Repos recommandé : {recommended}s",
    }


def get_fatigue_level(user_id: str, params: dict) -> dict:
    """Calculate current fatigue level based on recent training load."""
    sessions_table = get_table("sessions")

    # Get sessions from last 7 days
    today = datetime.now(timezone.utc).date()
    week_ago = (today - timedelta(days=7)).isoformat()

    response = sessions_table.query(
        KeyConditionExpression="userId = :uid AND sessionId > :start",
        ExpressionAttributeValues={
            ":uid": user_id,
            ":start": week_ago,
        },
    )

    sessions = response.get("Items", [])
    total_volume = sum(int(s.get("totalReps", 0)) for s in sessions)
    total_sessions = len(sessions)

    # Calculate fatigue (0 to 1)
    level = params.get("level", "intermediate")
    max_volume = MAX_WEEKLY_VOLUME.get(level, 600)
    fatigue = min(1.0, total_volume / max_volume)

    # Determine recommendation
    if fatigue > 0.9:
        recommendation = "⚠️ Fatigue très élevée. Jour de repos obligatoire recommandé."
        should_rest = True
    elif fatigue > 0.7:
        recommendation = "⚡ Fatigue modérée. Séance légère ou récupération active conseillée."
        should_rest = False
    elif fatigue > 0.4:
        recommendation = "✅ Bonne forme. Vous pouvez vous entraîner normalement."
        should_rest = False
    else:
        recommendation = "💪 Frais et reposé. Séance intense possible !"
        should_rest = False

    return {
        "fatigueLevel": round(fatigue, 2),
        "weeklyVolume": total_volume,
        "maxWeeklyVolume": max_volume,
        "sessionsThisWeek": total_sessions,
        "shouldRest": should_rest,
        "recommendation": recommendation,
    }


def get_recovery_session(user_id: str, params: dict) -> dict:
    """Suggest a recovery/active rest session."""
    return {
        "type": "recovery",
        "name": "Récupération active",
        "duration_minutes": 20,
        "exercises": [
            {"name": "Étirements dynamiques", "duration": "5 min"},
            {"name": "Mobilité épaules", "duration": "3 min"},
            {"name": "Mobilité hanches", "duration": "3 min"},
            {"name": "Foam rolling (si disponible)", "duration": "5 min"},
            {"name": "Respiration profonde", "duration": "4 min"},
        ],
        "message": "Séance de récupération active pour favoriser la régénération musculaire.",
    }


def handle(user_id: str, intent: str, params: dict) -> dict:
    """Agent Repos entry point."""
    if intent in ("timer", "rest_time", "repos", "temps"):
        return get_rest_time(user_id, params)
    elif intent in ("fatigue", "état", "récupération"):
        return get_fatigue_level(user_id, params)
    elif intent in ("recovery", "stretching", "mobilité"):
        return get_recovery_session(user_id, params)
    else:
        return get_fatigue_level(user_id, params)
