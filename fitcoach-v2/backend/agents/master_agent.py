"""
Master Agent — Orchestrateur du système multi-agents.
Route les requêtes vers les agents spécialisés et coordonne les réponses.
"""
import json
import sys
sys.path.insert(0, "/opt/python")
sys.path.insert(0, "..")

from shared.bedrock import invoke_llm_json
from shared.response import success, error

from agents.program_agent import handle as program_handle
from agents.calendar_agent import handle as calendar_handle
from agents.performance_agent import handle as performance_handle
from agents.rest_agent import handle as rest_handle
from agents.coach_agent import handle as coach_handle


ROUTING_SYSTEM = """Tu es le Master Agent de FitCoach AI. Tu dois analyser la requête utilisateur et déterminer quel agent spécialisé doit la traiter.

Agents disponibles :
- "program" : Génération et gestion de programmes d'entraînement
- "calendar" : Planification, vue semaine/mois, rappels
- "performance" : Suivi des stats, graphiques, PR, historique
- "rest" : Temps de repos, fatigue, récupération
- "coach" : Conseils, motivation, questions fitness générales
- "multi" : Si la requête nécessite plusieurs agents

Réponds UNIQUEMENT en JSON : {"agent": "nom_agent", "intent": "description courte", "params": {}}
Si "multi", ajoute "agents": ["agent1", "agent2"] dans params.
"""


AGENT_HANDLERS = {
    "program": program_handle,
    "calendar": calendar_handle,
    "performance": performance_handle,
    "rest": rest_handle,
    "coach": coach_handle,
}


def route_request(user_message: str, user_id: str, context: dict) -> dict:
    """Use LLM to determine which agent should handle the request."""
    prompt = f"""Requête utilisateur : "{user_message}"
Contexte : {json.dumps(context)}
Quel agent doit traiter cette requête ?"""

    try:
        routing = invoke_llm_json(prompt, system=ROUTING_SYSTEM, max_tokens=256)
        return routing
    except Exception:
        return {"agent": "coach", "intent": "fallback", "params": {}}


def execute_agent(agent_name: str, user_id: str, intent: str, params: dict) -> dict:
    """Execute the appropriate agent handler."""
    handler = AGENT_HANDLERS.get(agent_name)
    if not handler:
        return {"message": "Agent non trouvé", "agent": agent_name}

    return handler(user_id=user_id, intent=intent, params=params)


def handle_multi(agents: list, user_id: str, intent: str, params: dict) -> dict:
    """Handle multi-agent requests by aggregating responses."""
    results = {}
    for agent_name in agents:
        results[agent_name] = execute_agent(agent_name, user_id, intent, params)
    return {"type": "multi", "results": results}


def handler(event, context):
    """Lambda handler — Master Agent entry point."""
    try:
        body = json.loads(event.get("body", "{}"))
        user_id = body.get("userId", "anonymous")
        message = body.get("message", "")
        ctx = body.get("context", {})

        if not message:
            return error("Message requis", 400)

        # Route the request
        routing = route_request(message, user_id, ctx)
        agent_name = routing.get("agent", "coach")
        intent = routing.get("intent", "")
        params = routing.get("params", {})

        # Execute
        if agent_name == "multi":
            agents_list = params.get("agents", ["coach"])
            result = handle_multi(agents_list, user_id, intent, params)
        else:
            result = execute_agent(agent_name, user_id, intent, params)

        return success({
            "routing": routing,
            "response": result,
        })

    except Exception as e:
        return error(f"Erreur Master Agent: {str(e)}")
