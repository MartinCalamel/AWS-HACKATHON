import json
import math
import boto3

# All articulations needed for pushups, squats, plank
ARTICULATIONS = {
    "CoudeDroit": [12, 14, 16],
    "CoudeGauche": [11, 13, 15],
    "HancheDroite": [12, 24, 26],
    "HancheGauche": [11, 23, 25],
    "GenouDroit": [24, 26, 28],
    "GenouGauche": [23, 25, 27],
    "EpauleDroite": [11, 12, 14],
    "EpauleGauche": [12, 11, 13],
}


def get_angle(landmarks, point_a, point_b, point_c):
    a, b, c = landmarks[point_a], landmarks[point_b], landmarks[point_c]
    if a["visibility"] < 0.5 or b["visibility"] < 0.5 or c["visibility"] < 0.5:
        return None
    ab = [b["x"] - a["x"], b["y"] - a["y"]]
    bc = [b["x"] - c["x"], b["y"] - c["y"]]
    norm_ab = math.hypot(*ab)
    norm_bc = math.hypot(*bc)
    if norm_ab == 0 or norm_bc == 0:
        return None
    dot = (ab[0]*bc[0] + ab[1]*bc[1]) / (norm_ab * norm_bc)
    return math.degrees(math.acos(max(-1.0, min(1.0, dot))))


def handler(event, context):
    route = event["requestContext"]["routeKey"]
    if route in ("$connect", "$disconnect"):
        return {"statusCode": 200}

    if route == "sendframe":
        body = json.loads(event.get("body", "{}"))
        landmarks = body.get("landmarks")

        angles = {}
        if landmarks:
            for name, (a, b, c) in ARTICULATIONS.items():
                angles[name] = get_angle(landmarks, a, b, c)

        connection_id = event["requestContext"]["connectionId"]
        domain = event["requestContext"]["domainName"]
        stage = event["requestContext"]["stage"]
        apigw = boto3.client("apigatewaymanagementapi",
                             endpoint_url=f"https://{domain}/{stage}")
        apigw.post_to_connection(ConnectionId=connection_id,
                                 Data=json.dumps({"angles": angles}).encode())
        return {"statusCode": 200}

    return {"statusCode": 400}
