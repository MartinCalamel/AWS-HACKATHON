"""
Lambda handler pour l'analyse de posture via webcam.
Utilise Amazon Rekognition pour détecter les landmarks du corps
et évaluer la qualité de l'exercice.
"""
import json
import base64
import math
import boto3

rekognition = boto3.client("rekognition", region_name="us-east-1")

# Mapping des landmarks Rekognition utiles
# Voir: https://docs.aws.amazon.com/rekognition/latest/dg/API_Pose.html
LANDMARK_NAMES = {
    "leftShoulder": "leftShoulder",
    "rightShoulder": "rightShoulder",
    "leftElbow": "leftElbow",
    "rightElbow": "rightElbow",
    "leftWrist": "leftWrist",
    "rightWrist": "rightWrist",
    "leftHip": "leftHip",
    "rightHip": "rightHip",
    "leftKnee": "leftKnee",
    "rightKnee": "rightKnee",
    "leftAnkle": "leftAnkle",
    "rightAnkle": "rightAnkle",
}

# Configuration des exercices avec les landmarks nécessaires
EXERCISE_CONFIG = {
    "pushups": {
        "name": "Pompes",
        "angles": {
            "elbow": {
                "points": ["leftShoulder", "leftElbow", "leftWrist"],
                "ideal_min": 70,
                "ideal_max": 160,
            },
            "hip": {
                "points": ["leftShoulder", "leftHip", "leftKnee"],
                "ideal_min": 160,
                "ideal_max": 180,
            },
        },
    },
    "squats": {
        "name": "Squats",
        "angles": {
            "knee": {
                "points": ["leftHip", "leftKnee", "leftAnkle"],
                "ideal_min": 70,
                "ideal_max": 170,
            },
            "hip": {
                "points": ["leftShoulder", "leftHip", "leftKnee"],
                "ideal_min": 70,
                "ideal_max": 170,
            },
        },
    },
    "curls": {
        "name": "Curls",
        "angles": {
            "elbow": {
                "points": ["leftShoulder", "leftElbow", "leftWrist"],
                "ideal_min": 30,
                "ideal_max": 160,
            },
        },
    },
}


def calculate_angle(ax, ay, bx, by, cx, cy):
    """Calcule l'angle au point B formé par les points A, B, C (en degrés)."""
    radians = math.atan2(cy - by, cx - bx) - math.atan2(ay - by, ax - bx)
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle


def get_feedback(exercise, angles):
    """Génère des conseils basés sur les angles détectés."""
    feedback = []

    if exercise == "pushups":
        hip_angle = angles.get("hip", 180)
        elbow_angle = angles.get("elbow", 90)

        if hip_angle < 160:
            feedback.append("Gardez le corps bien droit, évitez de cambrer les hanches.")
        if elbow_angle > 160:
            feedback.append("Descendez plus bas pour un mouvement complet.")
        if elbow_angle < 70:
            feedback.append("Attention à ne pas descendre trop bas, protégez vos épaules.")
        if not feedback:
            feedback.append("Excellente posture ! Continuez comme ça.")

    elif exercise == "squats":
        knee_angle = angles.get("knee", 90)
        hip_angle = angles.get("hip", 90)

        if knee_angle < 70:
            feedback.append("Vos genoux sont trop fléchis. Remontez légèrement.")
        if hip_angle < 70:
            feedback.append("Gardez le dos plus droit, ne vous penchez pas trop en avant.")
        if knee_angle > 150:
            feedback.append("Descendez plus bas pour activer pleinement les muscles.")
        if not feedback:
            feedback.append("Bonne profondeur de squat ! Gardez le dos droit.")

    elif exercise == "curls":
        elbow_angle = angles.get("elbow", 90)

        if elbow_angle > 160:
            feedback.append("Contractez davantage le biceps en haut du mouvement.")
        if elbow_angle < 30:
            feedback.append("Parfaite contraction ! Contrôlez la descente.")
        if not feedback:
            feedback.append("Bon mouvement ! Gardez le coude fixe contre le corps.")

    return feedback


def calculate_score(exercise, angles):
    """Calcule un score de posture de 0 à 100."""
    config = EXERCISE_CONFIG.get(exercise, {})
    angle_configs = config.get("angles", {})

    if not angle_configs:
        return 50

    total_score = 0
    count = 0

    for angle_name, angle_config in angle_configs.items():
        if angle_name in angles:
            angle_val = angles[angle_name]
            min_val = angle_config["ideal_min"]
            max_val = angle_config["ideal_max"]
            mid = (min_val + max_val) / 2
            range_val = (max_val - min_val) / 2

            distance = abs(angle_val - mid)
            score = max(0, 100 - (distance / range_val) * 50)
            total_score += score
            count += 1

    return int(total_score / count) if count > 0 else 50


def determine_phase(exercise, angles):
    """Détermine la phase actuelle de l'exercice."""
    if exercise == "pushups":
        elbow = angles.get("elbow", 90)
        if elbow < 100:
            return "down"
        elif elbow > 140:
            return "up"
    elif exercise == "squats":
        knee = angles.get("knee", 90)
        if knee < 100:
            return "down"
        elif knee > 150:
            return "up"
    elif exercise == "curls":
        elbow = angles.get("elbow", 90)
        if elbow < 60:
            return "contracted"
        elif elbow > 140:
            return "extended"
    return "transition"


def handler(event, context):
    """Lambda handler principal."""
    try:
        body = json.loads(event.get("body", "{}"))
        image_b64 = body.get("image", "")
        exercise = body.get("exercise", "pushups")

        # Retirer le préfixe data:image/jpeg;base64, si présent
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]

        # Décoder l'image
        image_bytes = base64.b64decode(image_b64)

        # Appel à Rekognition pour détecter la pose
        response = rekognition.detect_faces(
            Image={"Bytes": image_bytes},
            Attributes=["ALL"],
        )

        # Rekognition detect_faces ne donne pas les landmarks du corps.
        # On utilise detect_labels ou detect_custom_labels pour la pose.
        # Meilleure approche : utiliser detect_protective_equipment ou
        # directement les coordonnées via un modèle custom.
        
        # Alternative : utiliser Rekognition detect_faces pour la tête
        # et estimer la posture via les proportions.
        # 
        # MEILLEURE SOLUTION : Utiliser Amazon Bedrock avec Claude Vision
        # pour analyser la posture directement depuis l'image.

        # Appel à Bedrock Claude Vision pour l'analyse de posture
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

        prompt = f"""Analyse cette image d'une personne faisant l'exercice "{exercise}" (pompes/squats/curls).

Évalue la posture et réponds UNIQUEMENT en JSON valide avec ce format exact :
{{
  "angles": {{
    "elbow": <angle_en_degrés_estimé>,
    "hip": <angle_en_degrés_estimé>,
    "knee": <angle_en_degrés_estimé>
  }},
  "feedback": ["conseil 1", "conseil 2"],
  "score": <score_de_0_à_100>,
  "phase": "<up|down|transition|contracted|extended>",
  "detected": true
}}

Si tu ne peux pas détecter de personne, réponds :
{{"detected": false, "feedback": ["Impossible de détecter votre posture."], "score": 0, "phase": "unknown", "angles": {{}}}}

Sois précis sur les angles articulaires visibles. Pour les pompes, évalue le coude et la hanche. Pour les squats, le genou et la hanche. Pour les curls, le coude."""

        bedrock_response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
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

        bedrock_body = json.loads(bedrock_response["body"].read())
        text = bedrock_body["content"][0]["text"]

        # Parser le JSON
        json_start = text.find("{")
        json_end = text.rfind("}") + 1
        analysis = json.loads(text[json_start:json_end])

        if not analysis.get("detected", True):
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
                    "feedback": analysis.get("feedback", ["Posture non détectée."]),
                    "score": 0,
                    "phase": "unknown",
                }),
            }

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
                "score": analysis.get("score", 50),
                "phase": analysis.get("phase", "transition"),
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
