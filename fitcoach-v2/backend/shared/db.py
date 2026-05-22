"""
Shared DynamoDB helpers for all agents.
"""
import boto3
import os
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "us-east-1"))

TABLES = {
    "users": os.environ.get("USERS_TABLE", "fitcoach-users"),
    "programs": os.environ.get("PROGRAMS_TABLE", "fitcoach-programs"),
    "sessions": os.environ.get("SESSIONS_TABLE", "fitcoach-sessions"),
    "performance": os.environ.get("PERFORMANCE_TABLE", "fitcoach-performance"),
    "calendar": os.environ.get("CALENDAR_TABLE", "fitcoach-calendar"),
    "achievements": os.environ.get("ACHIEVEMENTS_TABLE", "fitcoach-achievements"),
    "leaderboard": os.environ.get("LEADERBOARD_TABLE", "fitcoach-leaderboard"),
}


def get_table(name: str):
    """Get a DynamoDB table resource."""
    return dynamodb.Table(TABLES[name])


def now_iso() -> str:
    """Return current UTC time as ISO string."""
    return datetime.now(timezone.utc).isoformat()
