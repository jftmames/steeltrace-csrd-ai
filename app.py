import streamlit as st
import json
from pathlib import Path
import os
import pandas as pd
from datetime import datetime
import scripts.pipeline_run as pipeline_run

# --- Configuración de Paths ---
# Asegúrate de que el CWD es la raíz del repo
ROOT_DIR = Path(__file__).parent.resolve()
os.chdir(ROOT_DIR)

DQ_REPORT_FILE  = ROOT_DIR / "data" / "dq_report.json"
KPI_FILE        = ROOT_DIR / "raga" / "kpis.json"
EEE_REPORT_FILE = ROOT_DIR / "ops" / "gate_report.json"
SLO_REPORT_FILE = ROOT_DIR / "ops" / "slo_report.json"
HITL_REPORT_FILE = ROOT_DIR / "ops" / "hitl_kappa.json"

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        st.error(f"Error al decodificar JSON en: {path}")
        return None

# Definimos una función para ejecutar el pipeline.
# Usamos st.cache_data para evitar la reejecución en cada interacción de Streamlit,
# pero el botón "Ejecutar Pipeline" forzará una limpieza del caché.
@st.cache_data
def run_pipeline():
    """Ejecuta el script de orquestación del pipeline."""
    st.info(f"Ejecutando pipeline completo... Esto tomará unos segundos.")
    
    try:
        # Llama a la función directamente en lugar de subprocess
        result = pipeline_run.run_all_steps()

        # Construye un string similar al stdout anterior para mostrar logs
        output = []
        all_ok = True
        for step in result["steps"]:
            status = "✅" if step["ok"] else "❌"
            output.append(f"{status} {step['name']} ({step['duration_sec']:.2f}s)")
            if step["stdout"]:
                output.append(step["stdout"])
            if not step["ok"]:
                all_ok = False
                output.append(f"ERROR in {step['name']}: {step['stderr']}")

        if all_ok:
            st.success("Pipeline ejecutado correctamente.")
        else:
            st.error("El pipeline falló en algunos pasos.")

        return "\n".join(output)

    except Exception as e:
        st.error(f"El pipeline falló con una excepción inesperada.")
        st.code(str(e))
        return None

# --- Interfaz Streamlit ---
st.set_page_config(layout="wide", page_title="STEELTRACE™ CSRD+AI PoC Reporte")

st.title("STEELTRACE™ CSRD+AI - Reporte de Validación 📊")
st.markdown("Verificación de la Gobernanza, DQ y Trazabilidad del PoC.")

# Botón para iniciar/re-ejecutar el pipeline
if st.button("Ejecutar Pipeline y Recargar Reportes", help="Esto ejecuta scripts/pipeline_run.py y actualiza todos los reportes."):
    run_pipeline.clear() # Limpia el caché para forzar la reejecución
    run_pipeline()

# --- Carga y Muestra de Artefactos ---

st.header("1. Control de Publicación (EEE-Gate)")
eee_report = load_json(EEE_REPORT_FILE)

if eee_report:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Decisión Global", eee_report["global_decision"].upper(),
                  help="Basado en el EEE-Score y el Threshold (0.70)")
    with col2:
        eee_score = eee_report["eee_score"]
        delta_val = eee_score - eee_report["threshold"]
        st.metric("EEE-Score", f"{eee_score:.4f}", f"{delta_val:.4f} vs Threshold",
                  delta_color=("inverse" if eee_score < eee_report["threshold"] else "normal"))
    with col3:
        ep_score = eee_report["components"]["epistemic"]
        ex_score = eee_report["components"]["explicit"]
        ev_score = eee_report["components"]["evidence"]
        st.markdown(f"**Ponderaciones (Ep:0.4, Ex:0.3, Ev:0.3)**")
        st.progress(ep_score, text=f"Epistemicidad ({ep_score:.2f})")
        st.progress(ex_score, text=f"Explicitación ({ex_score:.2f})")
        st.progress(ev_score, text=f"Evidencia ({ev_score:.2f})")
    
    st.subheader("Detalle por KPI (RAGA)")
    kpi_data = load_json(KPI_FILE)
    if kpi_data:
        # Combina KPIs con las decisiones del gate
        kpi_list = [{"DP": d["dp"], "Valor": kpi_data.get(d["dp"]), "Decisión EEE": d["decision"]} 
                    for d in eee_report["details"]]
        st.dataframe(kpi_list, use_container_width=True, hide_index=True)


st.header("2. Data Quality (DQ) y Conformidad")
dq_report = load_json(DQ_REPORT_FILE)
if dq_report:
    st.metric("DQ Global Pass", str(dq_report["dq_pass"]), help="True si todos los dominios pasan el 95% DQ.")
    
    # Muestra tasas agregadas por dominio
    dq_summary = {
        dom: {
            "Conformidad": str(rep["dq"]["aggregate"]["dq_pass"]),
            "Completitud": f"{rep['dq']['aggregate']['completeness']:.2f}",
            "Validez": f"{rep['dq']['aggregate']['validity']:.2f}",
            "Consistencia": f"{rep['dq']['aggregate']['consistency']:.2f}",
            "Temporalidad": f"{rep['dq']['aggregate']['timeliness']:.2f}"
        } for dom, rep in dq_report["domains"].items()
    }
    st.subheader("Tasas Agregadas por Dominio")
    st.dataframe(dq_summary, use_container_width=True)

st.header("3. Observabilidad (SLO p95) y Gobernanza (HITL)")
slo_report = load_json(SLO_REPORT_FILE)
hitl_report = load_json(HITL_REPORT_FILE)

if slo_report:
    st.subheader("Métricas de Servicio (SLO p95)")
    # El script pipeline_run.py escribe agg como un diccionario, lo cargamos como DataFrame
    slo_df = pd.DataFrame(slo_report["agg"]).T
    slo_df.columns = ["Conteo", "P95 (segundos)", "Media (segundos)"]
    st.dataframe(slo_df, use_container_width=True)

if hitl_report:
    st.subheader("Acuerdo Inter-Evaluador (HITL)")
    mean_kappa = hitl_report.get("kappa_mean", "N/A")
    st.metric("Kappa de Cohen (Media)", f"{mean_kappa}", 
              help="Mide la concordancia entre los revisores humanos (Target: >0.70)")
    st.write("**Detalle de Kappa (por par):**")
    st.json(hitl_report["kappas"])

st.markdown("---")
st.warning("Para auditoría: Ver el paquete ZIP generado en `release/audit/` que contiene todos los artefactos firmados con Merkle Root.")
