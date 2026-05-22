"""
Lambda handler pour l'analyse de posture via webcam.
Utilise Amazon Bedrock Claude 3 Haiku (Vision) pour analyser la posture
et évaluer la qualité de l'exercice.

512 MB | 30s timeout
"""
import json
import base64
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")


def get_analysis_prompt(exercise):
    """Construit le prompt d'analyse de posture pour Claude Vision."""
    exercise_details = {
        "pushups": {
            "name": "pompes (push-ups)",
            "focus": "angle du coude (idéal: 90° en bas, 170° en haut) et alignement du corps (hanches alignées avec épaules et chevilles)",
        },
        "squats": {
            "name": "squats",
            "focus": "angle du genou (idéal: 90° en bas, 170° en haut) et angle de la hanche (dos droit, pas trop penché en avant)",
        },
        "curls": {
            "name": "curls de biceps",
            "focus": "angle du coude (idéal: 30° en contraction, 160° en extension) et stabilité du coude (collé au corps)",
        },
    }

    details = exercise_details.get(exercise, exercise_details["pushups"])

    return f"""Tu es un coach sportif expert en biomécanique. Analyse cette image d'une personne faisant des {details['name']}.

Points d'attention : {details['focus']}

Réponds UNIQUEMENT en JSON valide (pas de texte avant ou après) avec ce format exact :
{{
  "score": <nombre_entier_de_0_à_100>,
  "phase": "<up|down|transition|contracted|extended|unknown>",
  "feedback": ["conseil 1", "conseil 2", "conseil 3"]
}}

Règles :
- score : 0-100 basé sur la qualité de la posture (100 = parfait)
- phase : la phase actuelle du mouvement
- feedback : 1 à 3 conseils concrets et encourageants en français

Si tu ne vois pas de personne ou ne peux pas analyser la posture :
{{"score": 0, "phase": "unknown", "feedback": ["Impossible de détecter votre posture. Assurez-vous d'être bien visible dans le cadre."]}}
"""


def handler(event, context):
    """Lambda handler principal."""
    try:
        body = json.loads(event.get("body", "{}"))
        image_b64 = body.get("image", "")
        exercise = body.get("exercise", "pushups")

        # Retirer le préfixe data:image/jpeg;base64, si présent
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]

        prompt = get_analysis_prompt(exercise)

        # Appel à Bedrock Claude 3 Haiku avec Vision
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    }
                ],
            }),
        )

        response_body = json.loads(response["body"].read())
        text = response_body["content"][0]["text"]

        # Parser le JSON de la réponse
        json_start = text.find("{")
        json_end = text.rfind("}") + 1
        analysis = json.loads(text[json_start:json_end])

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
            },
            "body": json.dumps({
                "repCount": 0,
                "feedback": analysis.get("feedback", []),
                "score": analysis.get("score", 0),
                "phase": analysis.get("phase", "unknown"),
            }),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
            },
            "body": json.dumps({
                "error": str(e),
                "feedback": ["Erreur lors de l'analyse. Réessayez."],
                "score": 0,
                "phase": "error",
                "repCount": 0,
            }),
        }
