"""
Serveur local Flask pour le développement.
Simule les endpoints API Gateway + Lambda.
"""
import json
import base64
import numpy as np
from io import BytesIO
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import mediapipe as mp

app = Flask(__name__)
CORS(app)

mp_pose = mp.solutions.pose

# ===== Configuration des exercices =====
EXERCISE_CONFIG = {
    "pushups": {
        "name": "Pompes",
        "key_angles": {
            "elbow": {"min": 70, "max": 160, "landmarks": [11, 13, 15]},
            "hip": {"min": 160, "max": 180, "landmarks": [11, 23, 25]},
        },
    },
    "squats": {
        "name": "Squats",
        "key_angles": {
            "knee": {"min": 70, "max": 170, "landmarks": [23, 25, 27]},
            "hip": {"min": 70, "max": 170, "landmarks": [11, 23, 25]},
        },
    },
    "curls": {
        "name": "Curls",
        "key_angles": {
            "elbow": {"min": 30, "max": 160, "landmarks": [11, 13, 15]},
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
            feedback.append("Excellente posture ! Continuez comme ça. 💪")

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
            feedback.append("Bonne profondeur de squat ! Gardez le dos droit. 🦵")

    elif exercise == "curls":
        elbow_angle = angles.get("elbow", 90)
        if elbow_angle > 160:
            feedback.append("Contractez davantage le biceps en haut du mouvement.")
        if elbow_angle < 30:
            feedback.append("Parfaite contraction ! Contrôlez la descente.")
        if not feedback:
            feedback.append("Bon mouvement ! Gardez le coude fixe contre le corps. 💪")

    return feedback


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


@app.route("/analyze-pose", methods=["POST"])
def analyze_pose():
    """Analyse la posture depuis une image webcam."""
    try:
        data = request.get_json()
        image_b64 = data.get("image", "")
        exercise = data.get("exercise", "pushups")

        # Retirer le préfixe data:image/...
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]

        # Décoder l'image
        image_data = base64.b64decode(image_b64)
        image = Image.open(BytesIO(image_data))
        image_rgb = image.convert("RGB")
        image_np = np.array(image_rgb)

        # Analyse avec MediaPipe
        with mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.5,
        ) as pose:
            results = pose.process(image_np)

        if not results.pose_landmarks:
            return jsonify({
                "repCount": 0,
                "feedback": [
                    "Impossible de détecter votre posture.",
                    "Assurez-vous d'être bien visible dans le cadre.",
                    "Reculez un peu pour que tout votre corps soit visible.",
                ],
                "score": 0,
                "phase": "unknown",
            })

        # Extraire les landmarks et calculer les angles
        landmarks = results.pose_landmarks.landmark
        config = EXERCISE_CONFIG.get(exercise, {})
        angles = {}

        for angle_name, angle_config in config.get("key_angles", {}).items():
            lm = angle_config["landmarks"]
            a = [landmarks[lm[0]].x, landmarks[lm[0]].y]
            b = [landmarks[lm[1]].x, landmarks[lm[1]].y]
            c = [landmarks[lm[2]].x, landmarks[lm[2]].y]
            angles[angle_name] = calculate_angle(a, b, c)

        feedback = get_feedback(exercise, angles)
        score = calculate_score(exercise, angles)

        # Déterminer la phase
        phase = "transition"
        if exercise == "pushups":
            elbow = angles.get("elbow", 90)
            phase = "down" if elbow < 100 else "up" if elbow > 140 else "transition"
        elif exercise == "squats":
            knee = angles.get("knee", 90)
            phase = "down" if knee < 100 else "up" if knee > 150 else "transition"
        elif exercise == "curls":
            elbow = angles.get("elbow", 90)
            phase = "contracted" if elbow < 60 else "extended" if elbow > 140 else "transition"

        return jsonify({
            "repCount": 0,
            "feedback": feedback,
            "score": score,
            "phase": phase,
        })

    except Exception as e:
        return jsonify({
            "repCount": 0,
            "feedback": [f"Erreur: {str(e)}"],
            "score": 0,
            "phase": "error",
        }), 500


@app.route("/generate-planning", methods=["POST"])
def generate_planning():
    """Génère un planning d'exercices (version locale sans Bedrock)."""
    data = request.get_json()
    level = data.get("level", "beginner")
    goal = data.get("goal", "general")
    days_per_week = data.get("daysPerWeek", 3)

    # Multipliers selon le niveau
    reps_mult = {"beginner": 1, "intermediate": 1.3, "advanced": 1.6}.get(level, 1)
    sets_mult = {"beginner": 1, "intermediate": 1.2, "advanced": 1.5}.get(level, 1)

    # Templates par objectif
    templates = {
        "general": [
            {"day": "Jour 1 - Haut du corps", "exercises": [
                {"name": "Pompes", "sets": 3, "reps": 10, "rest": "60s"},
                {"name": "Dips", "sets": 3, "reps": 8, "rest": "60s"},
                {"name": "Curls", "sets": 3, "reps": 12, "rest": "45s"},
            ]},
            {"day": "Jour 2 - Bas du corps", "exercises": [
                {"name": "Squats", "sets": 4, "reps": 12, "rest": "60s"},
                {"name": "Fentes", "sets": 3, "reps": 10, "rest": "60s"},
                {"name": "Planche", "sets": 3, "reps": 30, "rest": "30s"},
            ]},
            {"day": "Jour 3 - Full body", "exercises": [
                {"name": "Pompes", "sets": 3, "reps": 12, "rest": "45s"},
                {"name": "Squats", "sets": 3, "reps": 15, "rest": "45s"},
                {"name": "Curls", "sets": 3, "reps": 10, "rest": "45s"},
            ]},
            {"day": "Jour 4 - Intensif", "exercises": [
                {"name": "Pompes", "sets": 4, "reps": 15, "rest": "30s"},
                {"name": "Squats", "sets": 4, "reps": 20, "rest": "30s"},
                {"name": "Fentes", "sets": 3, "reps": 12, "rest": "45s"},
            ]},
            {"day": "Jour 5 - Endurance", "exercises": [
                {"name": "Pompes", "sets": 5, "reps": 20, "rest": "20s"},
                {"name": "Squats", "sets": 5, "reps": 25, "rest": "20s"},
                {"name": "Planche", "sets": 4, "reps": 45, "rest": "15s"},
            ]},
        ],
        "strength": [
            {"day": "Jour 1 - Push", "exercises": [
                {"name": "Pompes", "sets": 5, "reps": 8, "rest": "90s"},
                {"name": "Dips", "sets": 4, "reps": 6, "rest": "90s"},
                {"name": "Pompes diamant", "sets": 3, "reps": 6, "rest": "90s"},
            ]},
            {"day": "Jour 2 - Legs", "exercises": [
                {"name": "Squats", "sets": 5, "reps": 8, "rest": "90s"},
                {"name": "Fentes", "sets": 4, "reps": 8, "rest": "90s"},
                {"name": "Squats sautés", "sets": 3, "reps": 6, "rest": "90s"},
            ]},
            {"day": "Jour 3 - Pull", "exercises": [
                {"name": "Curls", "sets": 5, "reps": 8, "rest": "90s"},
                {"name": "Planche", "sets": 4, "reps": 45, "rest": "60s"},
                {"name": "Superman", "sets": 3, "reps": 12, "rest": "60s"},
            ]},
            {"day": "Jour 4 - Full body force", "exercises": [
                {"name": "Pompes", "sets": 4, "reps": 10, "rest": "75s"},
                {"name": "Squats", "sets": 4, "reps": 10, "rest": "75s"},
                {"name": "Curls", "sets": 4, "reps": 10, "rest": "75s"},
            ]},
            {"day": "Jour 5 - Explosif", "exercises": [
                {"name": "Pompes claquées", "sets": 4, "reps": 5, "rest": "120s"},
                {"name": "Squats sautés", "sets": 4, "reps": 6, "rest": "120s"},
                {"name": "Burpees", "sets": 3, "reps": 8, "rest": "90s"},
            ]},
        ],
        "endurance": [
            {"day": "Jour 1 - Circuit", "exercises": [
                {"name": "Pompes", "sets": 4, "reps": 20, "rest": "30s"},
                {"name": "Squats", "sets": 4, "reps": 25, "rest": "30s"},
                {"name": "Planche", "sets": 3, "reps": 60, "rest": "20s"},
            ]},
            {"day": "Jour 2 - Endurance haute", "exercises": [
                {"name": "Pompes", "sets": 5, "reps": 15, "rest": "20s"},
                {"name": "Curls", "sets": 5, "reps": 20, "rest": "20s"},
                {"name": "Dips", "sets": 4, "reps": 15, "rest": "25s"},
            ]},
            {"day": "Jour 3 - Endurance basse", "exercises": [
                {"name": "Squats", "sets": 5, "reps": 30, "rest": "20s"},
                {"name": "Fentes", "sets": 4, "reps": 20, "rest": "20s"},
                {"name": "Planche", "sets": 4, "reps": 45, "rest": "15s"},
            ]},
            {"day": "Jour 4 - HIIT", "exercises": [
                {"name": "Burpees", "sets": 5, "reps": 12, "rest": "15s"},
                {"name": "Squats sautés", "sets": 5, "reps": 15, "rest": "15s"},
                {"name": "Pompes", "sets": 5, "reps": 15, "rest": "15s"},
            ]},
            {"day": "Jour 5 - Récupération active", "exercises": [
                {"name": "Squats", "sets": 3, "reps": 15, "rest": "45s"},
                {"name": "Planche", "sets": 3, "reps": 30, "rest": "30s"},
                {"name": "Fentes", "sets": 3, "reps": 10, "rest": "45s"},
            ]},
        ],
        "muscle": [
            {"day": "Jour 1 - Pectoraux/Triceps", "exercises": [
                {"name": "Pompes", "sets": 4, "reps": 12, "rest": "75s"},
                {"name": "Pompes diamant", "sets": 3, "reps": 10, "rest": "75s"},
                {"name": "Dips", "sets": 4, "reps": 10, "rest": "75s"},
            ]},
            {"day": "Jour 2 - Jambes", "exercises": [
                {"name": "Squats", "sets": 5, "reps": 12, "rest": "75s"},
                {"name": "Fentes", "sets": 4, "reps": 12, "rest": "75s"},
                {"name": "Squats sumo", "sets": 3, "reps": 15, "rest": "60s"},
            ]},
            {"day": "Jour 3 - Biceps/Dos", "exercises": [
                {"name": "Curls", "sets": 5, "reps": 12, "rest": "60s"},
                {"name": "Superman", "sets": 4, "reps": 15, "rest": "45s"},
                {"name": "Planche", "sets": 3, "reps": 45, "rest": "45s"},
            ]},
            {"day": "Jour 4 - Épaules/Core", "exercises": [
                {"name": "Pompes pike", "sets": 4, "reps": 10, "rest": "75s"},
                {"name": "Planche latérale", "sets": 3, "reps": 30, "rest": "45s"},
                {"name": "Crunchs", "sets": 4, "reps": 20, "rest": "45s"},
            ]},
            {"day": "Jour 5 - Full body volume", "exercises": [
                {"name": "Pompes", "sets": 4, "reps": 15, "rest": "60s"},
                {"name": "Squats", "sets": 4, "reps": 15, "rest": "60s"},
                {"name": "Curls", "sets": 4, "reps": 15, "rest": "60s"},
            ]},
        ],
    }

    plan = templates.get(goal, templates["general"])[:days_per_week]

    # Ajuster selon le niveau
    for day in plan:
        for ex in day["exercises"]:
            ex["reps"] = int(ex["reps"] * reps_mult)
            ex["sets"] = int(ex["sets"] * sets_mult)

    return jsonify({"planning": plan})


if __name__ == "__main__":
    print("🏋️ FitCoach AI - Serveur local démarré")
    print("📍 http://localhost:3001")
    print("📹 Endpoints:")
    print("   POST /analyze-pose")
    print("   POST /generate-planning")
    app.run(host="0.0.0.0", port=3001, debug=True)
