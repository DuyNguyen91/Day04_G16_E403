from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import ROOT, now_iso, run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ARTIFACTS = ROOT / "artifacts"
PROMPT_PATH = ARTIFACTS / "system_prompt.md"
TOOLS_PATH = ARTIFACTS / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"
DEFAULT_MODEL = "google/gemma-4-26b-a4b-it:free"

load_lab_env(ROOT)


def new_transcript(version: str, provider_name: str, model: str) -> tuple[Path, dict[str, Any]]:
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = f"ui_{version}_{provider_name}_{stamp}"
    path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    artifact = build_artifact_version(version, PROMPT_PATH, TOOLS_PATH)
    data: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": model,
        "interface": "streamlit",
        "system_prompt": str(PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    write_transcript(path, data)
    return path, data


def reset_session(version: str, provider_name: str, model: str) -> None:
    path, transcript = new_transcript(version, provider_name, model)
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.transcript_path = path
    st.session_state.transcript = transcript
    st.session_state.config_key = (version, provider_name, model)


def render_trace(turn: dict[str, Any]) -> None:
    rounds = turn.get("rounds") or []
    if not rounds:
        return
    with st.expander(f"Tool trace · {len(rounds)} round(s)", expanded=False):
        for round_item in rounds:
            st.markdown(f"**Round {round_item['round']}**")
            if round_item.get("assistant_text"):
                st.caption(round_item["assistant_text"])
            calls = round_item.get("tool_calls") or []
            results = round_item.get("tool_results") or []
            if not calls:
                st.info("No tool call")
            for index, call in enumerate(calls):
                st.code(
                    json.dumps({"tool": call["name"], "args": call.get("args", {})}, ensure_ascii=False, indent=2),
                    language="json",
                )
                if index < len(results):
                    result = results[index]
                    payload = result.get("result")
                    if isinstance(payload, dict) and payload.get("error"):
                        st.error(payload)
                    else:
                        st.json(payload)


st.set_page_config(page_title="G16 Research Agent", page_icon="🔎", layout="wide")
st.title("🔎 G16 Research Agent")
st.caption("Live research with inspectable tool calls, results, and versioned transcripts.")

with st.sidebar:
    st.header("Run configuration")
    version = st.text_input("Artifact version", value="v3")
    provider_name = st.selectbox("Provider", ["groq", "openrouter", "openai", "anthropic", "gemini"])
    default_model = "qwen/qwen3.6-27b" if provider_name == "groq" else (DEFAULT_MODEL if provider_name == "openrouter" else "")
    model = st.text_input("Model", value=default_model)
    st.caption("Changing configuration starts a fresh versioned transcript.")
    if st.button("New conversation", use_container_width=True):
        reset_session(version, provider_name, model)
        st.rerun()

config_key = (version, provider_name, model)
if st.session_state.get("config_key") != config_key:
    reset_session(version, provider_name, model)

artifact = build_artifact_version(version, PROMPT_PATH, TOOLS_PATH)
col1, col2, col3 = st.columns(3)
col1.metric("Version", version)
col2.metric("Provider", provider_name)
col3.code(artifact.artifact_version, language=None)
st.caption(f"Transcript: {st.session_state.transcript_path}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("turn"):
            render_trace(message["turn"])

if user_text := st.chat_input("Ask for news, social posts, URL reading, or source auditing…"):
    with st.chat_message("user"):
        st.markdown(user_text)
    st.session_state.messages.append({"role": "user", "content": user_text})

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    declarations = load_tool_declarations(TOOLS_PATH)
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, 5),
        {"role": "user", "content": user_text},
    ]
    turn: dict[str, Any] = {
        "turn_index": len(st.session_state.transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("assistant"):
        try:
            with st.spinner("Researching…"):
                result = run_model_tool_loop(
                    provider=make_provider(provider_name),
                    messages=messages,
                    tools=to_openai_tools(declarations),
                    model=model or None,
                    max_tool_rounds=4,
                )
            turn.update(result)
            answer = result["assistant_text"] or "No response text returned."
            st.markdown(answer)
            render_trace(turn)
            st.session_state.history.extend([
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": answer},
            ])
        except Exception as exc:
            answer = "Provider request failed. See the trace-safe error below and try again."
            turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
            st.error(turn["error"])

    turn["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
    st.session_state.messages.append({"role": "assistant", "content": answer, "turn": turn})
