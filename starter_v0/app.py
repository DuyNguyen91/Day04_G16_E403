from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_session() -> None:
    defaults: dict[str, Any] = {
        "history": [],
        "display": [],
        "provider_name": "openrouter",
        "version_label": "v3",
        "max_tool_rounds": 4,
        "history_window": 5,
        "transcript_path": None,
        "artifact_version": None,
        "model": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_transcript(provider_name: str, version_label: str, model: str | None, artifact) -> Path:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = f"{version_label}_{provider_name}_{timestamp}"
    path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    payload = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(ARTIFACTS_DIR / "system_prompt.md"),
        "tools": str(ARTIFACTS_DIR / "tools.yaml"),
        "source": "streamlit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    write_transcript(path, payload)
    return path


def append_turn(path: Path, turn: dict[str, Any]) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["turns"].append(turn)
    write_transcript(path, data)


def render_tool_events(events: list[dict[str, Any]]) -> None:
    if not events:
        st.caption("No tool calls this turn.")
        return
    for index, event in enumerate(events, start=1):
        result = event.get("result") or {}
        status = "error" if isinstance(result, dict) and result.get("error") else "ok"
        with st.expander(f"{index}. {event.get('tool')} — {status}", expanded=True):
            st.markdown("**args**")
            st.json(event.get("args") or {})
            st.markdown("**result**")
            st.json(result)


def main() -> None:
    st.set_page_config(page_title="G16 Research Agent", layout="wide")
    ensure_session()

    st.title("G16 Research Agent")
    st.caption("Day04 tool-calling lab — request/response + tool trace + artifact version")

    with st.sidebar:
        st.header("Run config")
        st.session_state.provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"], index=0)
        st.session_state.version_label = st.text_input("Artifact version label", value=st.session_state.version_label)
        st.session_state.max_tool_rounds = st.number_input("Max tool rounds", min_value=1, max_value=8, value=4)
        st.session_state.history_window = st.number_input("History window (pairs)", min_value=1, max_value=10, value=5)
        if st.button("Reset chat"):
            st.session_state.history = []
            st.session_state.display = []
            st.session_state.transcript_path = None
            st.rerun()

    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    openai_tools = to_openai_tools(tool_declarations)
    artifact = build_artifact_version(
        st.session_state.version_label,
        ARTIFACTS_DIR / "system_prompt.md",
        ARTIFACTS_DIR / "tools.yaml",
    )
    st.session_state.artifact_version = artifact.artifact_version

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("artifact_version", artifact.artifact_version)
    with col_b:
        transcript_name = Path(st.session_state.transcript_path).name if st.session_state.transcript_path else "(new on first message)"
        st.metric("transcript", transcript_name)

    for message in st.session_state.display:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("tool_events") is not None:
                render_tool_events(message["tool_events"])
            if message.get("rounds"):
                st.caption(f"rounds: {len(message['rounds'])}")

    user_text = st.chat_input("Ask the research agent…")
    if not user_text:
        return

    provider = make_provider(st.session_state.provider_name)
    model = getattr(provider, "default_model", None)
    st.session_state.model = model

    if st.session_state.transcript_path is None:
        st.session_state.transcript_path = str(
            start_transcript(st.session_state.provider_name, st.session_state.version_label, model, artifact)
        )

    st.session_state.display.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, int(st.session_state.history_window)),
        {"role": "user", "content": user_text},
    ]

    turn: dict[str, Any] = {
        "turn_index": len(st.session_state.history) // 2 + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("assistant"):
        with st.spinner("Running tool loop…"):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=None,
                    max_tool_rounds=int(st.session_state.max_tool_rounds),
                )
                turn.update(result)
                assistant_text = result.get("assistant_text") or ""
                st.markdown(assistant_text)
                render_tool_events(result.get("tool_events") or [])
                st.caption(f"status={result.get('status')} | rounds={len(result.get('rounds') or [])}")
                st.session_state.history.append({"role": "user", "content": user_text})
                st.session_state.history.append({"role": "assistant", "content": assistant_text})
                st.session_state.display.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "tool_events": result.get("tool_events") or [],
                    "rounds": result.get("rounds") or [],
                })
            except Exception as exc:
                err = f"{type(exc).__name__}: {exc}"
                turn.update({"status": "provider_error", "error": err})
                st.error(err)
                st.session_state.display.append({"role": "assistant", "content": err, "tool_events": []})

    turn["ended_at"] = now_iso()
    append_turn(Path(st.session_state.transcript_path), turn)
    st.caption(f"Saved transcript: {st.session_state.transcript_path}")


if __name__ == "__main__":
    main()
