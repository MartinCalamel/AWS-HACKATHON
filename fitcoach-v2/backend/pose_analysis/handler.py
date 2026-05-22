"""
Lambda handler pour l'analyse de posture via webcam.
Utilise MediaPipe Pose pour détecter les landmarks du corps,
calcule les angles articulaires, compte les reps et donne un score.
"""
import json
import base64
import numpy as np
from io import BytesIO
from PIL import Image
import mediapipe as mp

mp_pose = mp.solutions.pose

# ===== EXERCISE CONFIGURATIONS =====
EXERCISES = {
    "pushups_standard": {
        "name": "Pompes standard",
        "key_angles": {
            "elbow": {"landmarks": [11, 13, 15], "ideal_range": [70, 160]},
            "hip": {"landmarks": [11, 23, 25], "ideal_range": [160, 180]},
        },
        "phases": {"down": {"elbow": (70, 100)}, "up": {"elbow": (140, 180)}},
        "tips": {
            "hip_low": "Gardez le corps bien droit, ne laissez pas les hanches descendre.",
            "elbow_high": "Descendez plus bas pour un mouvement complet.",
            "elbow_low": "Attention à ne pas descendre trop bas, protégez vos épaules.",
        },
    },
    "pushups_diamond": {
        "name": "Pompes diamant",
        "key_angles": {
            "elbow": {"landmarks": [11, 13, 15], "ideal_range": [60, 150]},
            "hip": {"landmarks": [11, 23, 25], "ideal_range": [160, 180]},
        },
        "phases": {"down": {"elbow": (60, 90)}, "up": {"elbow": (130, 170)}},
        "tips": {
            "elbow_flare": "Gardez les coudes près du corps pour cibler les triceps.",
        },
    },
    "squats_standard": {
        "name": "Squats standard",
        "key_angles": {
            "knee": {"landmarks": [23, 25, 27], "ideal_range": [70, 170]},
            "hip": {"landmarks": [11, 23, 25], "ideal_range": [70, 170]},
        },
        "phases": {"down": {"knee": (70, 100)}, "up": {"knee": (150, 180)}},
        "tips": {
            "knee_over_toe": "Attention, genoux trop en avant. Poussez les fesses en arrière.",
            "back_round": "Gardez le dos droit, ne vous penchez pas trop en avant.",
            "depth": "Descendez plus bas pour activer pleinement les muscles.",
        },
    },
    "squats_jump": {
        "name": "Squats sautés",
        "key_angles": {
            "knee": {"landmarks": [23, 25, 27], "ideal_range": [70, 170]},
            "hip": {"landmarks": [11, 23, 25], "ideal_range": [70, 170]},
        },
        "phases": {"down": {"knee": (70, 110)}, "up": {"knee": (160, 180)}},
        "tips": {
            "landing": "Atterrissez en douceur, genoux légèrement fléchis.",
        },
    },
    "dips_standard": {
        "name": "Dips",
        "key_angles": {
            "elbow": {"landmarks": [11, 13, 15], "ideal_range": [70, 160]},
            "shoulder": {"landmarks": [13, 11, 23], "ideal_range": [0, 90]},
        },
        "phases": {"down": {"elbow": (70, 100)}, "up": {"elbow": (140, 170)}},
        "tips": {
            "lean_forward": "Penchez-vous légèrement en avant pour cibler les pectoraux.",
        },
    },
    "pullups": {
        "name": "Tractions",
        "key_angles": {
            "elbow": {"landmarks": [11, 13, 15], "ideal_range": [30, 170]},
        },
        "phases": {"up": {"elbow": (30, 70)}, "down": {"elbow": (140, 180)}},
        "tips": {
            "full_extension": "Descendez complètement bras tendus entre chaque rep.",
            "chin_over": "Montez jusqu'à ce que le menton dépasse la barre.",
        },
    },
    "plank": {
        "name": "Planche",
        "key_angles": {
            "hip": {"landmarks": [11, 23, 25], "ideal_range": [165, 180]},
            "shoulder": {"landmarks": [13, 11, 23], "ideal_range": [80, 100]},
        },
        "phases": {"hold": {"hip": (165, 180)}},
        "tips": {
            "hip_sag": "Ne laissez pas les hanches descendre, contractez les abdos.",
            "hip_pike": "Ne montez pas les fesses trop haut, restez aligné.",
        },
    },
    "lunges": {
        "name": "Fentes",
        "key_angles": {
            "front_knee": {"landmarks": [23, 25, 27], "ideal_range": [80, 100]},
            "back_knee": {"landmarks": [24, 26, 28], "ideal_range": [80, 100]},
        },
        "phases": {"down": {"front_knee": (80, 100)}, "up": {"front_knee": (150, 180)}},
        "tips": {
            "knee_forward": "Le genou avant ne doit pas dépasser la pointe du pied.",
        },
    },
}


def calculate_angle(a, b, c) -> float:
    """Calculate angle between three points in degrees."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180.0 else angle


def get_feedback(exercise_key: str, angles: dict) -> list:
    """Generate feedback based on detected angles."""
    config = EXERCISES.get(exercise_key, {})
    feedback = []

    if exercise_key.startswith("pushups"):
        hip = angles.get("hip", 180)
        elbow = angles.get("elbow", 90)
        if hip < 160:
            feedback.append(config.get("tips", {}).get("hip_low", "Gardez le corps aligné."))
        if elbow > 160:
            feedback.append(config.get("tips", {}).get("elbow_high", "Descendez plus bas."))
        if elbow < 60:
            feedback.append(config.get("tips", {}).get("elbow_low", "Ne descendez pas trop bas."))

    elif exercise_key.startswith("squats"):
        knee = angles.get("knee", 90)
        hip = angles.get("hip", 90)
        if knee < 70:
            feedback.append("Genoux trop fléchis, remontez légèrement.")
        if hip < 70:
            feedback.append(config.get("tips", {}).get("back_round", "Dos trop penché."))
        if knee > 150:
            feedback.append(config.get("tips", {}).get("depth", "Descendez plus bas."))

    elif exercise_key == "plank":
        hip = angles.get("hip", 180)
        if hip < 165:
            feedback.append(config.get("tips", {}).get("hip_sag", "Hanches trop basses."))
        if hip > 185:
            feedback.append(config.get("tips", {}).get("hip_pike", "Fesses trop hautes."))

    if not feedback:
        feedback.append("✅ Excellente posture ! Continuez comme ça.")

    return feedback


def determine_phase(exercise_key: str, angles: dict) -> str:
    """Determine current movement phase."""
    config = EXERCISES.get(exercise_key, {})
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


def calculate_score(exercise_key: str, angles: dict) -> int:
    """Calculate posture score 0-100."""
    config = EXERCISES.get(exercise_key, {})
    key_angles = config.get("key_angles", {})

    if not key_angles:
        return 50

    total_score = 0
    count = 0

    for angle_name, angle_config in key_angles.items():
        if angle_name in angles:
            angle_val = angles[angle_name]
            min_val, max_val = angle_config["ideal_range"]
            mid = (min_val + max_val) / 2
            range_val = (max_val - min_val) / 2
            distance = abs(angle_val - mid)
            score = max(0, 100 - (distance / range_val) * 50)
            total_score += score
            count += 1

    return int(total_score / count) if count > 0 else 50


def handler(event, context):
    """Lambda handler — Pose Analysis."""
    try:
        body = json.loads(event.get("body", "{}"))
        image_b64 = body.get("image", "")
        exercise = body.get("exercise", "pushups_standard")
        prev_phase = body.get("prevPhase", "")
        rep_count = body.get("repCount", 0)

        # Decode image
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]

        image_data = base64.b64decode(image_b64)
        image = Image.open(BytesIO(image_data)).convert("RGB")
        image_np = np.array(image)

        # MediaPipe analysis
        with mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.5,
        ) as pose:
            results = pose.process(image_np)

        if not results.pose_landmarks:
            return _response(200, {
                "repCount": rep_count,
                "feedback": ["Impossible de détecter votre posture. Assurez-vous d'être bien visible."],
                "score": 0,
                "phase": "unknown",
                "detected": False,
            })

        # Extract landmarks and calculate angles
        landmarks = results.pose_landmarks.landmark
        config = EXERCISES.get(exercise, EXERCISES["pushups_standard"])
        angles = {}

        for angle_name, angle_config in config.get("key_angles", {}).items():
            lm = angle_config["landmarks"]
            a = [landmarks[lm[0]].x, landmarks[lm[0]].y]
            b = [landmarks[lm[1]].x, landmarks[lm[1]].y]
            c = [landmarks[lm[2]].x, landmarks[lm[2]].y]
            angles[angle_name] = calculate_angle(a, b, c)

        # Determine phase and count reps
        phase = determine_phase(exercise, angles)
        new_rep_count = rep_count

        # Count rep on phase transition (down→up or up→down depending on exercise)
        if exercise.startswith("pullups"):
            if prev_phase == "up" and phase == "down":
                new_rep_count += 1
        else:
            if prev_phase == "down" and phase == "up":
                new_rep_count += 1

        # Generate feedback and score
        feedback = get_feedback(exercise, angles)
        score = calculate_score(exercise, angles)

        return _response(200, {
            "repCount": new_rep_count,
            "feedback": feedback,
            "score": score,
            "phase": phase,
            "angles": {k: round(v, 1) for k, v in angles.items()},
            "detected": True,
        })

    except Exception as e:
        return _response(500, {
            "error": str(e),
            "feedback": ["Erreur interne du serveur."],
            "score": 0,
            "phase": "error",
            "repCount": body.get("repCount", 0) if "body" in dir() else 0,
            "detected": False,
        })


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
        },
        "body": json.dumps(body, ensure_ascii=False),
    }
