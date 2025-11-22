import json, time
from pathlib import Path
from statistics import quantiles
from datetime import datetime

# Import steps directly
import scripts.mcp_ingest as mcp_ingest
import scripts.shacl_validate as shacl_validate
import scripts.raga_compute as raga_compute
import scripts.eee_gate as eee_gate
import scripts.xbrl_generate as xbrl_generate
import scripts.evidence_build as evidence_build

STEPS = [
    ("MCP.ingest",      mcp_ingest.run_ingest),
    ("SHACL.validate",  shacl_validate.run_shacl_validation),
    ("RAGA.compute",    raga_compute.run_raga),
    ("EEE.gate",        eee_gate.run_gate),
    ("XBRL.generate",   xbrl_generate.run_xbrl),
    ("EVIDENCE.build",  evidence_build.run_evidence)
]

SLO_FILE = Path("ops/slo_report.json")
HISTORY  = Path("ops/slo_history.jsonl")

def run_step(name, func):
    t0 = time.perf_counter()
    logs = []
    err_msg = ""
    ok = True

    try:
        result = func()
        if result["status"] == "error":
            ok = False
            err_msg = result.get("message", "Unknown error")
            logs.extend(result.get("logs", []))
        else:
            logs.extend(result.get("logs", []))
    except Exception as e:
        ok = False
        err_msg = str(e)

    t1 = time.perf_counter()
    dur = t1 - t0

    # Format output similar to subprocess capture
    stdout = "\n".join(logs)
    stderr = err_msg

    return {
        "name": name,
        "ok": ok,
        "duration_sec": dur,
        "stdout": stdout[-4000:],
        "stderr": stderr[-4000:]
    }

def p95(values):
    if not values:
        return None
    if len(values) < 20:
        # con pocas muestras usamos el max como aproximación
        return max(values)
    return quantiles(values, n=100)[94]

def aggregate(history):
    # history: lista de runs con pasos y duraciones
    agg = {}
    for run in history:
        for s in run["steps"]:
            agg.setdefault(s["name"], []).append(s["duration_sec"])
    return {k: {"count": len(v), "p95_sec": round(p95(v), 4), "mean_sec": round(sum(v)/len(v), 4)} for k,v in agg.items()}

def run_all_steps():
    Path("ops").mkdir(exist_ok=True)
    steps_results = [run_step(n, f) for n, f in STEPS]

    run = {"utc": datetime.utcnow().isoformat()+"Z", "steps": steps_results}

    # Append to history
    with open(HISTORY, "a", encoding="utf-8") as f:
        f.write(json.dumps(run) + "\n")

    # reconstruir historia
    hist = []
    if HISTORY.exists():
        for line in HISTORY.read_text(encoding="utf-8").splitlines():
            try:
                hist.append(json.loads(line))
            except Exception:
                pass

    agg = aggregate(hist)
    SLO_FILE.write_text(json.dumps({"utc": run["utc"], "agg": agg, "last_run": steps_results}, indent=2, ensure_ascii=False), encoding="utf-8")

    # Return the last run results for immediate display/check
    return run

def main():
    print("Running pipeline...")
    result = run_all_steps()

    all_ok = all(s["ok"] for s in result["steps"])
    if all_ok:
        print("Pipeline executed successfully.")
        print("SLO report →", SLO_FILE)
    else:
        print("Pipeline failed.")
        for s in result["steps"]:
            if not s["ok"]:
                print(f"Step failed: {s['name']}")
                print(f"Error: {s['stderr']}")

if __name__ == "__main__":
    main()
