import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.agent.prompts import SYSTEM_PROMPT
from app.models import ToolTraceEntry
from app.tools.registry import GEMINI_TOOLS, execute_tool
from app.tools.profile_memory import get_buyer_profile, clear_buyer_profile, update_buyer_profile

_ENV_PATH = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)
load_dotenv()

MAX_ITERATIONS = 8
MAX_HISTORY_TURNS = 12

_sessions: dict[str, list[types.Content]] = {}


def _get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
    return genai.Client(api_key=api_key)


def _model_name() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _trim_history(history: list[types.Content]) -> list[types.Content]:
    if len(history) <= MAX_HISTORY_TURNS * 2:
        return history
    return history[-(MAX_HISTORY_TURNS * 2) :]


def _extract_function_calls(response: types.GenerateContentResponse) -> list[types.FunctionCall]:
    calls: list[types.FunctionCall] = []
    if not response.candidates:
        return calls
    for part in response.candidates[0].content.parts or []:
        if part.function_call:
            calls.append(part.function_call)
    return calls


def _extract_text(response: types.GenerateContentResponse) -> str:
    if not response.candidates:
        return "I couldn't generate a response. Please try again."
    parts = response.candidates[0].content.parts or []
    texts = [p.text for p in parts if p.text]
    return "\n".join(texts) if texts else "I couldn't generate a response. Please try again."


def run_agent(session_id: str, user_message: str) -> tuple[str, list[ToolTraceEntry], list[dict]]:
    client = _get_client()
    history = _sessions.setdefault(session_id, [])

    history.append(types.Content(role="user", parts=[types.Part(text=user_message)]))
    history = _trim_history(history)

    tool_trace: list[ToolTraceEntry] = []
    properties_out: list[dict] = []
    
    # Get current buyer profile and inject it into system instructions
    profile = get_buyer_profile(session_id)
    profile_summary = []
    if profile.get("city"): profile_summary.append(f"City: {profile['city']}")
    if profile.get("max_budget_inr"): profile_summary.append(f"Max Budget: {profile['max_budget_inr']} INR")
    if profile.get("min_bhk"): profile_summary.append(f"Min BHK: {profile['min_bhk']}")
    if profile.get("locality"): profile_summary.append(f"Preferred Locality: {profile['locality']}")
    if profile.get("office_landmark"): profile_summary.append(f"Office/Landmark: {profile['office_landmark']}")
    if profile.get("must_have_tags"): profile_summary.append(f"Stated Tags: {', '.join(profile['must_have_tags'])}")
    
    profile_note = ""
    if profile_summary:
        profile_note = f"\n\n## Persistent Buyer Profile Memory (Core Preferences):\n" + "\n".join(f"- {item}" for item in profile_summary) + "\nAlways respect these preferences. If search criteria change, update the profile accordingly."

    contents: list[Any] = [
        types.Content(role="user", parts=[types.Part(text=SYSTEM_PROMPT + profile_note)]),
        *history,
    ]

    for _ in range(MAX_ITERATIONS):
        response = client.models.generate_content(
            model=_model_name(),
            contents=contents,
            config=types.GenerateContentConfig(tools=GEMINI_TOOLS, temperature=0.4),
        )

        function_calls = _extract_function_calls(response)
        if not function_calls:
            reply = _extract_text(response)
            history.append(types.Content(role="model", parts=[types.Part(text=reply)]))
            _sessions[session_id] = history
            return reply, tool_trace, properties_out

        function_response_parts: list[types.Part] = []
        for fc in function_calls:
            name = fc.name or "unknown"
            args = dict(fc.args) if fc.args else {}
            
            if name == "update_buyer_profile":
                args["session_id"] = session_id
                
            result, summary = execute_tool(name, args)

            tool_trace.append(
                ToolTraceEntry(tool=name, args=args, result_summary=summary)
            )

            if name == "search_properties" and isinstance(result, dict) and "properties" in result:
                # Deduplicate by ID if multiple searches happen
                existing_ids = {p["id"] for p in properties_out}
                for p in result["properties"]:
                    if p["id"] not in existing_ids:
                        properties_out.append(p)
            elif name == "get_property_details" and isinstance(result, dict) and "error" not in result:
                existing_ids = {p["id"] for p in properties_out}
                if result.get("id") and result["id"] not in existing_ids:
                    properties_out.append(result)

            function_response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=name,
                        response={"result": result},
                    )
                )
            )

        contents.append(response.candidates[0].content)
        contents.append(types.Content(role="user", parts=function_response_parts))

    reply = (
        "I gathered some data but need another message to finalize recommendations. "
        "Please ask me to summarize what I found so far."
    )
    history.append(types.Content(role="model", parts=[types.Part(text=reply)]))
    _sessions[session_id] = history
    return reply, tool_trace, properties_out


def reset_session(session_id: str) -> None:
    _sessions.pop(session_id, None)
    clear_buyer_profile(session_id)
