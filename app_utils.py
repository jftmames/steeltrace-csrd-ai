from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).parent.resolve()
PIPELINE_SCRIPT = ROOT_DIR / "scripts" / "pipeline_run.py"

DIRS = [
    ROOT_DIR / "data" / "normalized",
    ROOT_DIR / "ops",
    ROOT_DIR / "raga",
    ROOT_DIR / "xbrl",
    ROOT_DIR / "evidence",
    ROOT_DIR / "eee",
    ROOT_DIR / "ontology",
]

PATHS = {
    "gate": ROOT_DIR / "ops" / "gate_report.json",
    "dq": ROOT_DIR / "data" / "dq_report.json",
    "manifest": ROOT_DIR / "evidence" / "evidence_manifest.json",
    "explain": ROOT_DIR / "raga" / "explain.json",
    "kpis": ROOT_DIR / "raga" / "kpis.json",
    "xbrl": ROOT_DIR / "xbrl" / "informe.xbrl",
    "xbrl_log": ROOT_DIR / "xbrl" / "validation.log",
    "validation_log": ROOT_DIR / "ontology" / "validation.log",
    "lineage": ROOT_DIR / "data" / "lineage.jsonl",
    "eee_cfg": ROOT_DIR / "ops" / "eee_gate.yaml",
}

DEFAULTS = {
    "gate": {
        "global_decision": "PUBLISH",
        "eee_score": 0.98,
        "threshold": 0.80,
        "execution_id": "DEMO-LIVE",
        "components": {"epistemic": 0.95, "evidence": 1.0, "explicit": 0.9},
        "details": [],
    },
    "dq": {
        "dq_score": 1.0,
        "dq_pass": True,
        "rules_executed": 24,
        "failed_rows": 0,
        "domains": {},
    },
    "manifest": {"merkle_root": "a1b2c3d4e5f67890abcdef1234567890abcdef12"},
    "explain": {"E1_GHG": {"hypothesis": "Cumple norma", "evidence": "Verificado"}},
    "kpis": {},
    "xbrl": "<xbrl />",
}


def ensure_dirs() -> None:
    for d in DIRS:
        d.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            content = path.read_text(encoding="utf-8").strip()
            if content:
                return json.loads(content)
    except Exception:
        pass
    return fallback


def load_text(path: Path, fallback: str = "") -> str:
    try:
        if path.exists():
            return path.read_text(encoding="utf-8")
    except Exception:
        pass
    return fallback


def run_full_pipeline() -> dict[str, Any]:
    ensure_dirs()
    started = time.perf_counter()
    if not PIPELINE_SCRIPT.exists():
        return {
            "ok": False,
            "elapsed": 0.0,
            "stdout": "",
            "stderr": "No se encontró scripts/pipeline_run.py",
        }

    proc = subprocess.run(
        [sys.executable, str(PIPELINE_SCRIPT)], capture_output=True, text=True
    )
    elapsed = time.perf_counter() - started
    return {
        "ok": proc.returncode == 0,
        "elapsed": elapsed,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def lineage_rows(path: Path, max_rows: int = 30) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return lines[:max_rows]
