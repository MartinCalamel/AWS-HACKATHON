"""
Agent Programme — Génération et gestion de programmes d'entraînement personnalisés.
"""
import json
import uuid
from shared.bedrock import invoke_llm_json
from shared.db import get_table, now_iso


PROGRAM_SYSTEM = """Tu es un coach sportif expert en musculation au poids du corps.
Tu génères des programmes d'entraînement personnalisés.

Exercices disponibles : Pompes (standard, diamant, déclinées, archer), Squats (standard, pistol, jump, sumo),
Dips (standard, bench), Tractions (pull-up, chin-up, wide), Planche (standard, latérale),
Fentes (standard, marchées, sautées), Burpees, Mountain climbers.

Réponds UNIQUEMENT en JSON valide avec ce format :
{
  "name": "Nom du programme",
  "description": "Description courte",
  "duration_weeks": 4,
  "days_per_week": 3,
  "weeks": [
    {
      "week": 1,
      "days": [
        {
          "day": "Jour 1 - Full Body",
          "exercises": [
            {"name": "Pompes standard", "sets": 3, "reps": 12, "rest_seconds": 60, "tempo": "2-1-2"}
          ]
        }
      ]
    }
  ]
}

Adapte les séries, reps et variantes au niveau. Inclus une progression sur 4 semaines.
Semaine 4 = deload (volume réduit de 40%).
"""


def generate_program(user_id: str, params: dict) -> dict:
    """Generate a personalized training program."""
    level = params.get("level", "beginner")
    goal = params.get("goal", "general")
    days_per_week = params.get("daysPerWeek", 3)
    limitations = params.get("limitations", [])

    prompt = f"""Génère un programme d'entraînement poids du corps.
Profil :
- Niveau : {level}
- Objectif : {goal}
- Jours par semaine : {days_per_week}
- Limitations physiques : {', '.join(limitations) if limitations else 'Aucune'}

Génère un programme complet de 4 semaines avec progression."""

    program_data = invoke_llm_json(prompt, system=PROGRAM_SYSTEM, max_tokens=4096)

    # Save to DynamoDB
    program_id = f"prog_{uuid.uuid4().hex[:8]}"
    table = get_table("programs")
    table.put_item(Item={
        "userId": user_id,
        "programId": program_id,
        "createdAt": now_iso(),
        "level": level,
        "goal": goal,
        "daysPerWeek": days_per_week,
        "data": json.dumps(program_data, ensure_ascii=False),
        "active": True,
    })

    return {
        "programId": program_id,
        "program": program_data,
        "message": f"Programme '{program_data.get('name', 'Custom')}' créé avec succès.",
    }


def get_program(user_id: str, params: dict) -> dict:
    """Retrieve a specific program."""
    program_id = params.get("programId")
    table = get_table("programs")

    response = table.get_item(Key={"userId": user_id, "programId": program_id})
    item = response.get("Item")

    if not item:
        return {"error": "Programme non trouvé"}

    return {
        "programId": item["programId"],
        "program": json.loads(item["data"]),
        "createdAt": item["createdAt"],
    }


def list_programs(user_id: str) -> dict:
    """List all programs for a user."""
    table = get_table("programs")
    response = table.query(
        KeyConditionExpression="userId = :uid",
        ExpressionAttributeValues={":uid": user_id},
    )
    programs = []
    for item in response.get("Items", []):
        data = json.loads(item["data"])
        programs.append({
            "programId": item["programId"],
            "name": data.get("name", "Sans nom"),
            "createdAt": item["createdAt"],
            "active": item.get("active", False),
        })
    return {"programs": programs}


def handle(user_id: str, intent: str, params: dict) -> dict:
    """Agent Programme entry point."""
    if intent in ("generate", "create", "créer", "générer"):
        return generate_program(user_id, params)
    elif intent in ("get", "voir", "détail"):
        return get_program(user_id, params)
    elif intent in ("list", "liste", "mes programmes"):
        return list_programs(user_id)
    else:
        return generate_program(user_id, params)
