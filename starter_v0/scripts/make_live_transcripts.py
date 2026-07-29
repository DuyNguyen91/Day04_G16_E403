"""Generate required live-chat transcripts without interactive stdin."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chat import run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ARTIFACTS = ROOT / "artifacts"
OUT = ROOT / "transcripts"
load_lab_env(ROOT)


SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "research_normal",
        "slug": "live_research",
        "turns": ["Tin AI hôm nay có gì nổi bật trên web?"],
    },
    {
        "name": "missing_then_fill",
        "slug": "live_clarify",
        "turns": [
            "Tóm tắt 5 tweet mới nhất giúp mình",
            "Của Sam Altman nhé",
        ],
    },
    {
        "name": "send_boundary",
        "slug": "live_boundary",
        "turns": ["Đăng bản tin AI này lên Telegram giúp mình"],
    },
]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def run_scenario(scenario: dict[str, Any], *, version: str = "v3") -> Path:
    system_prompt = (ARTIFACTS / "system_prompt.md").read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(ARTIFACTS / "tools.yaml"))
    provider = make_provider("openrouter")
    model = getattr(provider, "default_model", None)
    artifact = build_artifact_version(version, ARTIFACTS / "system_prompt.md", ARTIFACTS / "tools.yaml")

    transcript_id = f"{version}_openrouter_01095_PHANTRONGTIEN_{scenario['slug']}"
    path = OUT / f"{transcript_id}.transcript.json"
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        "scenario": scenario["name"],
        **artifact_version_dict(artifact),
        "provider": "openrouter",
        "model": model,
        "system_prompt": str(ARTIFACTS / "system_prompt.md"),
        "tools": str(ARTIFACTS / "tools.yaml"),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

    history: list[dict[str, str]] = []
    for index, user_text in enumerate(scenario["turns"], start=1):
        print(f"[{scenario['name']}] turn {index}: {user_text}")
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(history, 5),
            {"role": "user", "content": user_text},
        ]
        turn: dict[str, Any] = {
            "turn_index": index,
            "started_at": now_iso(),
            "user": user_text,
        }
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=tools,
            model=None,
            max_tool_rounds=4,
        )
        turn.update(result)
        turn["ended_at"] = now_iso()
        transcript["turns"].append(turn)
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": result.get("assistant_text") or ""})
        print(f"  status={result.get('status')} tools={[e.get('tool') for e in result.get('tool_events') or []]}")

    write_transcript(path, transcript)
    print(f"Saved {path}")
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for scenario in SCENARIOS:
        run_scenario(scenario)


if __name__ == "__main__":
    main()
