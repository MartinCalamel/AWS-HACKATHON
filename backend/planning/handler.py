"""
Lambda handler pour la génération de planning d'exercices.
Utilise Amazon Bedrock (Claude 3 Haiku) pour créer des programmes personnalisés.

256 MB | 30s timeout
"""
import json
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")


def generate_planning_prompt(level, goal, days_per_week):
    """Construit le prompt pour Bedrock."""
    level_fr = {
        "beginner": "débutant",
        "intermediate": "intermédiaire",
        "advanced": "avancé",
    }.get(level, "débutant")

    goal_fr = {
        "general": "forme générale",
        "strength": "force",
        "endurance": "endurance",
        "muscle": "prise de masse musculaire",
    }.get(goal, "forme générale")

    return f"""Tu es un coach sportif professionnel. Génère un planning d'exercices hebdomadaire.

Profil de l'utilisateur :
- Niveau : {level_fr}
- Objectif : {goal_fr}
- Disponibilité : {days_per_week} jours par semaine

Les exercices disponibles sont : Pompes, Squats, Curls (biceps), Planche, Fentes, Dips.

Réponds UNIQUEMENT en JSON valide avec ce format exact (pas de texte avant ou après) :
{{
  "planning": [
    {{
      "day": "Jour 1 - Haut du corps",
      "exercises": [
        {{"name": "Pompes", "sets": 3, "reps": 12, "rest": "60s"}}
      ]
    }}
  ]
}}

Génère exactement {days_per_week} jours d'entraînement. Adapte les séries et répétitions au niveau {level_fr}.
"""


def generate_fallback_planning(days):
    """Planning par défaut si Bedrock n'est pas disponible."""
    base_plans = [
        {
            "day": "Jour 1 - Haut du corps",
            "exercises": [
                {"name": "Pompes", "sets": 3, "reps": 10, "rest": "60s"},
                {"name": "Dips", "sets": 3, "reps": 8, "rest": "60s"},
                {"name": "Curls", "sets": 3, "reps": 12, "rest": "45s"},
            ],
        },
        {
            "day": "Jour 2 - Bas du corps",
            "exercises": [
                {"name": "Squats", "sets": 4, "reps": 12, "rest": "60s"},
                {"name": "Fentes", "sets": 3, "reps": 10, "rest": "60s"},
                {"name": "Planche", "sets": 3, "reps": 1, "rest": "30s"},
            ],
        },
        {
            "day": "Jour 3 - Full body",
            "exercises": [
                {"name": "Pompes", "sets": 3, "reps": 12, "rest": "45s"},
                {"name": "Squats", "sets": 3, "reps": 15, "rest": "45s"},
                {"name": "Curls", "sets": 3, "reps": 10, "rest": "45s"},
                {"name": "Planche", "sets": 2, "reps": 1, "rest": "30s"},
            ],
        },
        {
            "day": "Jour 4 - Intensif",
            "exercises": [
                {"name": "Pompes", "sets": 4, "reps": 15, "rest": "30s"},
                {"name": "Squats", "sets": 4, "reps": 20, "rest": "30s"},
                {"name": "Dips", "sets": 3, "reps": 12, "rest": "45s"},
                {"name": "Fentes", "sets": 3, "reps": 12, "rest": "45s"},
            ],
        },
        {
            "day": "Jour 5 - Endurance",
            "exercises": [
                {"name": "Pompes", "sets": 5, "reps": 20, "rest": "20s"},
                {"name": "Squats", "sets": 5, "reps": 25, "rest": "20s"},
                {"name": "Planche", "sets": 4, "reps": 1, "rest": "15s"},
            ],
        },
    ]
    return base_plans[:days]


def handler(event, context):
    """Lambda handler principal."""
    days_per_week = 3
    try:
        body = json.loads(event.get("body", "{}"))
        level = body.get("level", "beginner")
        goal = body.get("goal", "general")
        days_per_week = body.get("daysPerWeek", 3)

        prompt = generate_planning_prompt(level, goal, days_per_week)

        # Appel à Bedrock (Claude 3 Haiku)
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            }),
        )

        response_body = json.loads(response["body"].read())
        assistant_message = response_body["content"][0]["text"]

        # Parser le JSON de la réponse
        json_start = assistant_message.find("{")
        json_end = assistant_message.rfind("}") + 1
        planning_json = json.loads(assistant_message[json_start:json_end])

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
            },
            "body": json.dumps(planning_json),
        }

    except Exception as e:
        # Fallback : planning par défaut
        fallback = generate_fallback_planning(days_per_week)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
            },
            "body": json.dumps({"planning": fallback}),
        }
