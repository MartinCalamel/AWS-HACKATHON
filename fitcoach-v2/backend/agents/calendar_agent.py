"""
Agent Calendrier — Planification des séances et gestion de l'agenda.
"""
import json
from datetime import datetime, timedelta, timezone
from shared.db import get_table, now_iso


def get_week(user_id: str, params: dict) -> dict:
    """Get the training schedule for the current or specified week."""
    table = get_table("calendar")
    today = datetime.now(timezone.utc).date()
    start_of_week = today - timedelta(days=today.weekday())

    # Query 7 days
    days = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        date_str = day.isoformat()
        response = table.get_item(Key={"userId": user_id, "date": date_str})
        item = response.get("Item")
        days.append({
            "date": date_str,
            "dayName": day.strftime("%A"),
            "session": json.loads(item["session"]) if item and "session" in item else None,
            "isRest": item.get("isRest", False) if item else True,
            "completed": item.get("completed", False) if item else False,
        })

    return {"week": days, "startDate": start_of_week.isoformat()}


def schedule_session(user_id: str, params: dict) -> dict:
    """Schedule a training session on a specific date."""
    table = get_table("calendar")
    date = params.get("date")
    session_data = params.get("session", {})

    if not date:
        return {"error": "Date requise"}

    table.put_item(Item={
        "userId": user_id,
        "date": date,
        "session": json.dumps(session_data, ensure_ascii=False),
        "isRest": False,
        "completed": False,
        "createdAt": now_iso(),
    })

    return {"message": f"Séance planifiée le {date}", "date": date}


def reschedule(user_id: str, params: dict) -> dict:
    """Reschedule a missed session to the next available day."""
    table = get_table("calendar")
    original_date = params.get("date")
    new_date = params.get("newDate")

    if not original_date or not new_date:
        return {"error": "Dates requises (date, newDate)"}

    # Get original session
    response = table.get_item(Key={"userId": user_id, "date": original_date})
    item = response.get("Item")

    if not item:
        return {"error": "Aucune séance trouvée à cette date"}

    # Move to new date
    session_data = item.get("session", "{}")
    table.put_item(Item={
        "userId": user_id,
        "date": new_date,
        "session": session_data,
        "isRest": False,
        "completed": False,
        "rescheduledFrom": original_date,
        "createdAt": now_iso(),
    })

    # Mark original as rest
    table.update_item(
        Key={"userId": user_id, "date": original_date},
        UpdateExpression="SET isRest = :r, rescheduledTo = :d",
        ExpressionAttributeValues={":r": True, ":d": new_date},
    )

    return {"message": f"Séance reportée du {original_date} au {new_date}"}


def mark_completed(user_id: str, params: dict) -> dict:
    """Mark a session as completed."""
    table = get_table("calendar")
    date = params.get("date", datetime.now(timezone.utc).date().isoformat())

    table.update_item(
        Key={"userId": user_id, "date": date},
        UpdateExpression="SET completed = :c, completedAt = :t",
        ExpressionAttributeValues={":c": True, ":t": now_iso()},
    )

    return {"message": f"Séance du {date} marquée comme complétée"}


def handle(user_id: str, intent: str, params: dict) -> dict:
    """Agent Calendrier entry point."""
    if intent in ("week", "semaine", "planning"):
        return get_week(user_id, params)
    elif intent in ("schedule", "planifier", "ajouter"):
        return schedule_session(user_id, params)
    elif intent in ("reschedule", "reporter", "déplacer"):
        return reschedule(user_id, params)
    elif intent in ("complete", "terminer", "fait"):
        return mark_completed(user_id, params)
    else:
        return get_week(user_id, params)
