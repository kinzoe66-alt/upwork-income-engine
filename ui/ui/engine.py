from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

from rubric import detect_signals

@dataclass
class EvalResult:
    score: int
    decision: str
    hits: List[Dict[str, Any]]
    notes: List[str]
    ts_utc: str

def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))

def decide(score: int) -> str:
    # Tune thresholds as desired
    if score >= 70:
        return "ACCEPT"
    if score >= 45:
        return "REVIEW"
    return "REJECT"

def evaluate(text: str) -> EvalResult:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    hits = detect_signals(text)

    # Base score gives “not empty” submissions a starting floor
    base = 20 if len(text.strip()) >= 20 else 5

    total = base + sum(int(h["weight"]) for h in hits)
    score = clamp(total, 0, 100)

    notes = []
    if len(text.strip()) < 20:
        notes.append("Very short description (low signal).")
    if not any(h["key"] == "budget_present" for h in hits):
        notes.append("No explicit budget detected.")
    if any(h["weight"] < 0 for h in hits):
        notes.append("Risk flags detected; review before responding.")

    return EvalResult(score=score, decision=decide(score), hits=hits, notes=notes, ts_utc=ts)

def repo_root() -> Path:
    # ui/engine.py -> ui -> repo root
    return Path(__file__).resolve().parents[1]

def write_artifacts(job_text: str, result: EvalResult) -> Dict[str, str]:
    root = repo_root()

    logs_dir = root / "logs"
    reports_dir = root / "reports"
    exports_dir = root / "exports"

    logs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    exports_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    short_id = stamp

    # JSON export (structured)
    export_path = exports_dir / f"eval_{short_id}.json"
    payload = {
        "ts_utc": result.ts_utc,
        "score": result.score,
        "decision": result.decision,
        "hits": result.hits,
        "notes": result.notes,
        "job_text": job_text,
    }
    export_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Markdown report (human-readable)
    report_path = reports_dir / f"eval_{short_id}.md"
    lines = []
    lines.append(f"# Upwork Offer Evaluation\n")
    lines.append(f"- Timestamp (UTC): {result.ts_utc}")
    lines.append(f"- Score: **{result.score}**")
    lines.append(f"- Decision: **{result.decision}**\n")
    lines.append("## Signals Hit\n")
    if result.hits:
        for h in result.hits:
            w = h["weight"]
            lines.append(f"- `{h['key']}` ({w:+d})")
    else:
        lines.append("- (none)")
    lines.append("\n## Notes\n")
    if result.notes:
        for n in result.notes:
            lines.append(f"- {n}")
    else:
        lines.append("- (none)")
    lines.append("\n## Raw Job Text\n")
    lines.append("```")
    lines.append(job_text.rstrip())
    lines.append("```")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Append JSONL log line
    log_path = logs_dir / f"evals_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts_utc": result.ts_utc,
            "score": result.score,
            "decision": result.decision,
            "export_file": str(export_path.relative_to(root)).replace("\\", "/"),
            "report_file": str(report_path.relative_to(root)).replace("\\", "/"),
        }) + "\n")

    return {
        "export_file": str(export_path.relative_to(root)).replace("\\", "/"),
        "report_file": str(report_path.relative_to(root)).replace("\\", "/"),
        "log_file": str(log_path.relative_to(root)).replace("\\", "/"),
    }
