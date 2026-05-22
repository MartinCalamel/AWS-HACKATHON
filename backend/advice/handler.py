"""
Lambda handler pour la génération de conseils personnalisés via Bedrock.
Fournit des recommandations détaillées basées sur l'historique de posture.
"""
import json
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")


def handler(event, context):
    """Génère des conseils personnalisés basés sur les performances."""
    try:
        body = json.loads(event.get("body", "{}"))
        exercise = body.get("exercise", "pushups")
        scores = body.get("scores", [])
        common_issues = body.get("commonIssues", [])

        exercise_names = {
            "pushups": "pompes",
            "squats": "squats",
            "curls": "curls de biceps",
        }

        prompt = f"""Tu es un coach sportif bienveillant et expert. 
L'utilisateur fait des {exercise_names.get(exercise, exercise)}.

Ses scores récents de posture : {scores}
Problèmes fréquents détectés : {', '.join(common_issues) if common_issues else 'Aucun problème majeur'}

Donne 3-5 conseils concrets et encourageants pour améliorer sa technique.
Réponds en JSON : {{"advice": ["conseil 1", "conseil 2", ...]}}
"""

        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            }),
        )

        response_body = json.loads(response["body"].read())
        text = response_body["content"][0]["text"]

        json_start = text.find("{")
        json_end = text.rfind("}") + 1
        advice_json = json.loads(text[json_start:json_end])

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(advice_json),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "error": str(e),
                "advice": [
                    "Gardez une posture droite et contrôlée.",
                    "Respirez régulièrement pendant l'exercice.",
                    "Échauffez-vous avant chaque séance.",
                ],
            }),
        }
