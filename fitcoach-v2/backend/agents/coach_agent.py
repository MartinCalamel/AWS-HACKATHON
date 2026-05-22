"""
Agent Coach — Motivation, conseils personnalisés et communication naturelle.
"""
import json
from shared.bedrock import invoke_llm_json, invoke_llm
from shared.db import get_table, now_iso


COACH_SYSTEM = """Tu es un coach sportif bienveillant, motivant et expert en musculation au poids du corps.
Tu parles en français, de manière encourageante mais honnête.
Tu donnes des conseils concrets et actionnables.
Tu connais les exercices : pompes, squats, dips, tractions, planche, fentes, burpees, mountain climbers.
Tu ne donnes PAS de conseils médicaux. Si l'utilisateur mentionne une douleur, recommande de consulter un professionnel.

Réponds en JSON : {"message": "ton message", "tips": ["conseil1", "conseil2"]}
"""


BADGES = [
    {"id": "first_session", "name": "🔥 Premier pas", "condition": "Compléter sa première séance", "xp": 50},
    {"id": "perfect_form", "name": "💯 Perfectionniste", "condition": "Score posture > 90%", "xp": 100},
    {"id": "streak_7", "name": "📅 Régulier", "condition": "7 jours de streak", "xp": 150},
    {"id": "centurion", "name": "🏆 Centurion", "condition": "100 pompes en une séance", "xp": 200},
    {"id": "streak_30", "name": "⚡ Infatigable", "condition": "30 jours de streak", "xp": 500},
    {"id": "pr_10", "name": "🎯 Sniper", "condition": "10 PR battus", "xp": 300},
    {"id": "legend", "name": "👑 Légende", "condition": "Atteindre le niveau maximum", "xp": 1000},
]

LEVELS = [
    {"level": 1, "name": "Débutant", "xp_required": 0},
    {"level": 2, "name": "Apprenti", "xp_required": 500},
    {"level": 3, "name": "Régulier", "xp_required": 1500},
    {"level": 4, "name": "Athlète", "xp_required": 3500},
    {"level": 5, "name": "Expert", "xp_required": 7000},
    {"level": 6, "name": "Maître", "xp_required": 12000},
    {"level": 7, "name": "Légende", "xp_required": 20000},
]


def chat(user_id: str, params: dict) -> dict:
    """Handle a natural language conversation with the coach."""
    message = params.get("message", "")

    prompt = f"""L'utilisateur dit : "{message}"
Réponds de manière motivante et utile."""

    result = invoke_llm_json(prompt, system=COACH_SYSTEM, max_tokens=512)
    return result


def get_achievements(user_id: str, params: dict) -> dict:
    """Get user achievements, XP, and level."""
    table = get_table("achievements")

    response = table.query(
        KeyConditionExpression="userId = :uid",
        ExpressionAttributeValues={":uid": user_id},
    )

    unlocked = {item["badgeId"]: item for item in response.get("Items", [])}
    total_xp = sum(int(item.get("xp", 0)) for item in response.get("Items", []))

    # Calculate level
    current_level = LEVELS[0]
    for lvl in LEVELS:
        if total_xp >= lvl["xp_required"]:
            current_level = lvl

    next_level = None
    for lvl in LEVELS:
        if lvl["xp_required"] > total_xp:
            next_level = lvl
            break

    # Build badges list
    badges = []
    for badge in BADGES:
        badges.append({
            **badge,
            "unlocked": badge["id"] in unlocked,
            "unlockedAt": unlocked[badge["id"]].get("unlockedAt") if badge["id"] in unlocked else None,
        })

    return {
        "totalXp": total_xp,
        "level": current_level,
        "nextLevel": next_level,
        "xpToNextLevel": (next_level["xp_required"] - total_xp) if next_level else 0,
        "badges": badges,
        "streak": params.get("streak", 0),
    }


def unlock_badge(user_id: str, badge_id: str) -> dict:
    """Unlock a badge for the user."""
    table = get_table("achievements")
    badge = next((b for b in BADGES if b["id"] == badge_id), None)

    if not badge:
        return {"error": "Badge non trouvé"}

    table.put_item(Item={
        "userId": user_id,
        "badgeId": badge_id,
        "xp": badge["xp"],
        "unlockedAt": now_iso(),
    })

    return {
        "message": f"🎉 Badge débloqué : {badge['name']}",
        "badge": badge,
        "xpEarned": badge["xp"],
    }


def get_leaderboard(user_id: str, params: dict) -> dict:
    """Get the weekly leaderboard."""
    table = get_table("leaderboard")

    # Get current week key
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc)
    week_key = f"WEEKLY#{today.strftime('%Y-W%W')}"

    response = table.query(
        KeyConditionExpression="weekKey = :wk",
        ExpressionAttributeValues={":wk": week_key},
        ScanIndexForward=False,
        Limit=20,
    )

    leaderboard = []
    for i, item in enumerate(response.get("Items", []), 1):
        leaderboard.append({
            "rank": i,
            "userId": item.get("userId", ""),
            "username": item.get("username", "Anonyme"),
            "xp": int(item.get("weeklyXp", 0)),
            "isCurrentUser": item.get("userId") == user_id,
        })

    return {"leaderboard": leaderboard, "week": week_key}


def handle(user_id: str, intent: str, params: dict) -> dict:
    """Agent Coach entry point."""
    if intent in ("chat", "question", "conseil", "aide"):
        return chat(user_id, params)
    elif intent in ("achievements", "badges", "progression", "niveau"):
        return get_achievements(user_id, params)
    elif intent in ("leaderboard", "classement"):
        return get_leaderboard(user_id, params)
    elif intent in ("unlock", "badge"):
        badge_id = params.get("badgeId", "")
        return unlock_badge(user_id, badge_id)
    else:
        return chat(user_id, params)
