import json, os
from pathlib import Path
from datetime import datetime
from scripts.merkle import build_manifest

RUN_ID = os.environ.get("STEELTRACE_RUN_ID", "2025Q1-ACME-0001")

ARTIFACTS = [
    "raga/kpis.json",
    "raga/explain.json",
    "ontology/validation.log",
    "ontology/linaje.ttl",
    "ops/gate_report.json",
    "eee/eee_report.json",
    "xbrl/informe.xbrl",
    "xbrl/validation.log"
]

def run_evidence():
    logs = []
    try:
        Path("evidence/tokens").mkdir(parents=True, exist_ok=True)
        Path("evidence/verify").mkdir(parents=True, exist_ok=True)

        man = build_manifest(ARTIFACTS, RUN_ID)
        man["created_utc"] = datetime.utcnow().isoformat() + "Z"
        token = {
            "tsa": "SIMULATED-TSA",
            "ts_utc": datetime.utcnow().isoformat() + "Z",
            "merkle_root": man["merkle_root"]
        }
        man["tsa_tokens"] = [token]

        Path("evidence/evidence_manifest.json").write_text(json.dumps(man, indent=2, ensure_ascii=False))
        Path("evidence/tokens/2025Q1.tsr").write_text(json.dumps(token, indent=2))
        Path("evidence/verify/2025Q1.txt").write_text("Verification: OK (simulated)\n")
        logs.append("Evidence manifest → evidence/evidence_manifest.json")
        return {"status": "ok", "logs": logs}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    res = run_evidence()
    if res["status"] == "error":
        print(res["message"])
        exit(1)
    for log in res["logs"]:
        print(log)

if __name__ == "__main__":
    main()
