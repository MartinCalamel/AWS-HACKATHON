"""
Shared Bedrock client for LLM calls.
"""
import json
import boto3
import os

bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1"))

MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")


def invoke_llm(prompt: str, system: str = "", max_tokens: int = 2048) -> str:
    """Invoke Bedrock Claude and return the text response."""
    messages = [{"role": "user", "content": prompt}]

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": messages,
    }

    if system:
        body["system"] = system

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body),
    )

    response_body = json.loads(response["body"].read())
    return response_body["content"][0]["text"]


def invoke_llm_json(prompt: str, system: str = "", max_tokens: int = 2048) -> dict:
    """Invoke Bedrock Claude and parse JSON from the response."""
    text = invoke_llm(prompt, system, max_tokens)
    json_start = text.find("{")
    json_end = text.rfind("}") + 1
    if json_start == -1:
        json_start = text.find("[")
        json_end = text.rfind("]") + 1
    return json.loads(text[json_start:json_end])
