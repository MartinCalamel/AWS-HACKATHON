"""
Lambda handler pour l'analyse de posture via webcam.
Utilise MediaPipe Pose pour détecter les landmarks du corps
et évaluer la qualité de l'exercice.

512 MB | 30s timeout
"""
import json
import base64
import numpy as np
from io import BytesIO
from PIL import Image
import mediapipe as mp

mp_pose = mp.solutions.pose

# Angles idéaux par exercice
EXERCISE_CONFIG = {
    "pushups": {
        "name": "Pompes",
        "key_angles": {
            "elbow": {"min": 70, "max": 160, "landmarks": [11, 13, 15]},
            "hip": {"min": 160, "max": 180, "landmarks": [11, 23, 25]},
        },
        "phases": {
            "down": {"elbow": (70, 100)},
            "up": {"elbow": (140, 180)},
        },
    },
    "squats": {
        "name": "Squats",
        "key_angles": {
            "knee": {"min": 70, "max": 170, "landmarks": [23, 25, 27]},
            "hip": {"min": 70, "max": 170, "landmarks": [11, 23, 25]},
        },
        "phases": {
            "down": {"knee": (70, 100)},
            "up": {"knee": (150, 180)},
        },
    },
    "curls": {
        "name": "Curls",
        "key_angles": {
            "elbow": {"min": 30, "max": 160, "landmarks": [11, 13, 15]},
        },
        "phases": {
            "contracted": {"elbow": (30, 60)},
            "extended": {"elbow": (140, 170)},
        },
    },
}


def calculate_angle(a, b, c):
    """Calcule l'angle entre trois points (en degrés)."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(
        a[1] - b[1], a[0] - b[0]
    )
    angle = np.abs(radians * 180.0 / np.pi)

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
            feedback.append("Attention, vos genoux sont trop fléchis. Remontez légèrement.")
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


def determine_phase(exercise, angles):
    """Détermine la phase actuelle de l'exercice."""
    config = EXERCISE_CONFIG.get(exercise, {})
    phases = config.get("phases", {})

    for phase_name, phase_angles in phases.items():
        match = True
        for angle_name, (min_val, max_val) in phase_angles.items():
            if angle_name in angles:
                if not (min_val <= angles[angle_name] <= max_val):
                    match = False
                    break
        if match:
            return phase_name

    return "transition"


def calculate_score(exercise, angles):
    """Calcule un score de posture de 0 à 100."""
    config = EXERCISE_CONFIG.get(exercise, {})
    key_angles = config.get("key_angles", {})

    if not key_angles:
        return 50

    total_score = 0
    count = 0

    for angle_name, angle_config in key_angles.items():
        if angle_name in angles:
            angle_val = angles[angle_name]
            min_val = angle_config["min"]
            max_val = angle_config["max"]
            mid = (min_val + max_val) / 2
            range_val = (max_val - min_val) / 2

            distance = abs(angle_val - mid)
            score = max(0, 100 - (distance / range_val) * 50)
            total_score += score
            count += 1

    return int(total_score / count) if count > 0 else 50


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
        image_data = base64.b64decode(image_b64)
        image = Image.open(BytesIO(image_data))
        image_rgb = image.convert("RGB")
        image_np = np.array(image_rgb)

        # Analyse avec MediaPipe Pose
        with mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.5,
        ) as pose:
            results = pose.process(image_np)

        if not results.pose_landmarks:
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
                    "feedback": [
                        "Impossible de détecter votre posture.",
                        "Assurez-vous d'être bien visible dans le cadre.",
                    ],
                    "score": 0,
                    "phase": "unknown",
                }),
            }

        # Extraire les landmarks
        landmarks = results.pose_landmarks.landmark
        config = EXERCISE_CONFIG.get(exercise, {})

        # Calculer les angles articulaires
        angles = {}
        for angle_name, angle_config in config.get("key_angles", {}).items():
            lm = angle_config["landmarks"]
            a = [landmarks[lm[0]].x, landmarks[lm[0]].y]
            b = [landmarks[lm[1]].x, landmarks[lm[1]].y]
            c = [landmarks[lm[2]].x, landmarks[lm[2]].y]
            angles[angle_name] = calculate_angle(a, b, c)

        # Générer le résultat
        feedback = get_feedback(exercise, angles)
        phase = determine_phase(exercise, angles)
        score = calculate_score(exercise, angles)

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
                "feedback": feedback,
                "score": score,
                "phase": phase,
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
