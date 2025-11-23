import json, subprocess, time, sys
from pathlib import Path
from statistics import quantiles
from datetime import datetime

# Importamos la definición de pasos compartida
try:
    from scripts.pipeline_meta import STEPS
except ImportError:
    # Fallback si se ejecuta desde scripts/ directamente sin instalar como paquete
    sys.path.append(str(Path(__file__).parent.parent))
    from scripts.pipeline_meta import STEPS

SLO_FILE = Path("ops/slo_report.json")
HISTORY  = Path("ops/slo_history.jsonl")

def run_step(name, cmd):
    t0 = time.perf_counter()
    # Ejecutamos el subproceso capturando stdout/stderr
    proc = subprocess.run(cmd, capture_output=True, text=True)
    t1 = time.perf_counter()
    dur = t1 - t0
    ok  = proc.returncode == 0

    if not ok:
        print(f"[{name}] FAILED:")
        print(proc.stderr)
    else:
        print(f"[{name}] OK ({dur:.2f}s)")

    return {
        "name": name,
        "ok": ok,
        "duration_sec": dur,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:]
    }

def p95(values):
    if not values:
        return None
    if len(values) < 20:
        return max(values)
    return quantiles(values, n=100)[94]

def aggregate(history):
    agg = {}
    for run in history:
        for s in run["steps"]:
            agg.setdefault(s["name"], []).append(s["duration_sec"])
    return {k: {"count": len(v), "p95_sec": round(p95(v), 4), "mean_sec": round(sum(v)/len(v), 4)} for k,v in agg.items()}

def main():
    Path("ops").mkdir(exist_ok=True)

    steps_results = []
    for n, c in STEPS:
        res = run_step(n, c)
        steps_results.append(res)

    run = {"utc": datetime.utcnow().isoformat()+"Z", "steps": steps_results}

    current_history = HISTORY.read_text(encoding="utf-8") if HISTORY.exists() else ""
    HISTORY.write_text(current_history + json.dumps(run) + "\n", encoding="utf-8")

    hist = []
    if HISTORY.exists():
        for line in HISTORY.read_text(encoding="utf-8").splitlines():
            try:
                hist.append(json.loads(line))
            except Exception:
                pass

    agg = aggregate(hist)
    SLO_FILE.write_text(json.dumps({"utc": run["utc"], "agg": agg, "last_run": steps_results}, indent=2, ensure_ascii=False), encoding="utf-8")
    print("SLO report →", SLO_FILE)

if __name__ == "__main__":
    main()
