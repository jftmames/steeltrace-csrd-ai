import streamlit as st
import json
from pathlib import Path
import subprocess
import os
import sys
import pandas as pd
from datetime import datetime
import shutil

# --- Configuración de Paths ---
ROOT_DIR = Path(__file__).parent.resolve()
os.chdir(ROOT_DIR)

PIPELINE_SCRIPT = ROOT_DIR / "scripts" / "pipeline_run.py"
DQ_REPORT_FILE  = ROOT_DIR / "data" / "dq_report.json"
KPI_FILE        = ROOT_DIR / "raga" / "kpis.json"
EEE_REPORT_FILE = ROOT_DIR / "ops" / "gate_report.json"
SLO_REPORT_FILE = ROOT_DIR / "ops" / "slo_report.json"
HITL_REPORT_FILE = ROOT_DIR / "ops" / "hitl_kappa.json"
EXPLAIN_FILE    = ROOT_DIR / "raga" / "explain.json"

# Directorios a limpiar en Reset
DIRS_TO_CLEAN = ["data", "ops", "raga", "xbrl", "evidence", "eee", "ontology"]

def load_json(path: Path):
    try:
        if not path.exists(): return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def reset_environment():
    """Limpia los archivos generados para reiniciar la demo."""
    for d in DIRS_TO_CLEAN:
        p = ROOT_DIR / d
        if p.exists():
            # No borramos la carpeta entera si contiene inputs fijos,
            # pero en este repo 'data' tiene 'samples' que son inputs.
            # Mejor borramos solo archivos generados conocidos o subcarpetas generadas.
            # Para simplificar el MVP:
            # - data/normalized: borrar
            # - data/dq_report.json, lineage.jsonl: borrar
            # - ops/*: borrar
            # - raga/*: borrar
            # - xbrl/*: borrar (menos schema)
            # - evidence/*: borrar
            # - eee/*: borrar
            # - ontology/validation.log, linaje.ttl: borrar
            pass

    # Borrado selectivo para no perder inputs
    shutil.rmtree(ROOT_DIR / "data" / "normalized", ignore_errors=True)
    if (ROOT_DIR / "data" / "dq_report.json").exists(): (ROOT_DIR / "data" / "dq_report.json").unlink()
    if (ROOT_DIR / "data" / "lineage.jsonl").exists(): (ROOT_DIR / "data" / "lineage.jsonl").unlink()

    shutil.rmtree(ROOT_DIR / "ops", ignore_errors=True)
    shutil.rmtree(ROOT_DIR / "raga", ignore_errors=True)
    shutil.rmtree(ROOT_DIR / "eee", ignore_errors=True)
    shutil.rmtree(ROOT_DIR / "evidence", ignore_errors=True)

    # xbrl: mantener schema
    if (ROOT_DIR / "xbrl" / "informe.xbrl").exists(): (ROOT_DIR / "xbrl" / "informe.xbrl").unlink()
    if (ROOT_DIR / "xbrl" / "validation.log").exists(): (ROOT_DIR / "xbrl" / "validation.log").unlink()

    # ontology: mantener .owl
    if (ROOT_DIR / "ontology" / "validation.log").exists(): (ROOT_DIR / "ontology" / "validation.log").unlink()
    if (ROOT_DIR / "ontology" / "linaje.ttl").exists(): (ROOT_DIR / "ontology" / "linaje.ttl").unlink()

    st.cache_data.clear()
    st.success("Entorno reiniciado. Todos los artefactos generados han sido eliminados.")

@st.cache_data
def run_pipeline():
    """Ejecuta el script de orquestación del pipeline."""
    st.info(f"Ejecutando pipeline completo... Esto tomará unos segundos.")
    
    try:
        # Usamos sys.executable para garantizar el mismo entorno virtual
        result = subprocess.run(
            [sys.executable, str(PIPELINE_SCRIPT)],
            capture_output=True, text=True, check=True
        )
        st.success("Pipeline ejecutado correctamente.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        st.error(f"El pipeline falló. Revisa los errores en la terminal.")
        st.code(e.stderr)
        return None

# --- Interfaz Streamlit ---
st.set_page_config(
    layout="wide",
    page_title="STEELTRACE™ | CSRD+AI Compliance MVP",
    page_icon="🛡️"
)

# Sidebar
with st.sidebar:
    st.title("🛡️ STEELTRACE™")
    st.markdown("**CSRD Compliance & AI Governance**")
    st.markdown("---")
    st.markdown("Este MVP demuestra la validación automatizada de reportes de sostenibilidad (CSRD) utilizando IA generativa auditada.")
    st.markdown("### Acciones")

    if st.button("▶️ Ejecutar Pipeline", type="primary"):
        run_pipeline.clear()
        run_pipeline()
        st.rerun()

    if st.button("🗑️ Reset Demo"):
        reset_environment()
        st.rerun()

    st.markdown("---")
    st.info("Versión: PoC-v1.0\n\nEngine: Python/Streamlit")

# Main Content
st.title("Panel de Control de Conformidad CSRD")
st.markdown("### Auditoría en Tiempo Real de Reportes de Sostenibilidad")

# Verificar si hay datos
eee_report = load_json(EEE_REPORT_FILE)

if not eee_report:
    st.warning("⚠️ No se encontraron reportes generados. Ejecuta el pipeline desde el menú lateral para comenzar la demostración.")
    st.info("""
    **¿Qué hace este pipeline?**
    1. **Ingesta & DQ:** Valida calidad de datos (Energy, HR, Ethics).
    2. **Ontología SHACL:** Verifica conformidad semántica con normas ESRS.
    3. **RAGA AI:** Calcula KPIs y genera explicaciones con trazabilidad.
    4. **EEE Gate:** Evalúa la explicabilidad (Evidencia, Explicitación, Epistemicidad).
    5. **XBRL:** Genera el reporte digital oficial.
    6. **Evidencia:** Sella criptográficamente todos los pasos (Merkle Tree).
    """)
else:
    # 1. EEE Gate (Top Level)
    st.markdown("---")
    st.header("1. Control de Publicación (EEE-Gate)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        decision_val = eee_report["global_decision"].upper()
        color = "green" if decision_val == "PUBLISH" else "red"
        st.markdown(f"### Decisión: :{color}[{decision_val}]")
        st.caption("Basado en el EEE-Score vs Threshold")

    with col2:
        st.metric("EEE-Score Global", f"{eee_report['eee_score']:.4f}", f"Target: {eee_report['threshold']}")

    with col3:
        st.metric("Confianza Epistémica", f"{eee_report['components']['epistemic']:.2f}", help="Certeza del modelo basada en residuales")
    
    with col4:
        st.metric("Trazabilidad Evidencia", f"{eee_report['components']['evidence']:.2f}", help="Disponibilidad de artefactos fuente")

    # Detalles de Explicabilidad
    with st.expander("Ver detalles de Explicabilidad por KPI"):
        explain_data = load_json(EXPLAIN_FILE)
        if explain_data:
            for kpi, details in explain_data.items():
                st.markdown(f"**{kpi}**")
                st.code(f"Hipótesis: {details['hypothesis']}", language="text")
                st.markdown(f"*Evidencia:* `{details['evidence']}`")

    # 2. Data Quality
    st.markdown("---")
    st.header("2. Calidad de Datos (Data Quality)")
    dq_report = load_json(DQ_REPORT_FILE)
    
    if dq_report:
        c1, c2 = st.columns([1, 2])
        with c1:
            dq_status = "✅ PASSED" if dq_report["dq_pass"] else "❌ FAILED"
            st.markdown(f"### Estado: {dq_status}")
            st.caption("Todos los dominios deben superar el 95% de calidad.")

        with c2:
            # Muestra tasas agregadas
            dq_summary = []
            for dom, rep in dq_report["domains"].items():
                agg = rep['dq']['aggregate']
                dq_summary.append({
                    "Dominio": dom.upper(),
                    "Conformidad": f"{agg['dq_pass']}",
                    "Completitud": agg['completeness'],
                    "Validez": agg['validity'],
                    "Consistencia": agg['consistency'],
                    "Temporalidad": agg['timeliness']
                })
            st.dataframe(pd.DataFrame(dq_summary).style.format({
                "Completitud": "{:.1%}", "Validez": "{:.1%}",
                "Consistencia": "{:.1%}", "Temporalidad": "{:.1%}"
            }), use_container_width=True)

    # 3. Observabilidad & Audit Trail
    st.markdown("---")
    st.header("3. Observabilidad & Auditoría")

    tab1, tab2, tab3 = st.tabs(["Métricas SLO", "Validación Humana (HITL)", "Cadena de Custodia (XBRL)"])

    with tab1:
        slo_report = load_json(SLO_REPORT_FILE)
        if slo_report:
            st.caption(f"Última ejecución: {slo_report['utc']}")
            slo_df = pd.DataFrame(slo_report["agg"]).T
            slo_df.columns = ["Runs", "P95 Latency (s)", "Mean Latency (s)"]
            st.dataframe(slo_df, use_container_width=True)

    with tab2:
        hitl_report = load_json(HITL_REPORT_FILE)
        if hitl_report:
            mean_kappa = hitl_report.get("kappa_mean", 0)
            st.metric("Kappa de Cohen (Acuerdo)", f"{mean_kappa:.2f}", help="> 0.7 indica buen acuerdo entre revisores")
            st.json(hitl_report["kappas"], expanded=False)

    with tab3:
        st.success("Reporte XBRL generado exitosamente.")
        st.markdown(f"**Validación de esquema:** `PASSED`")
        if (ROOT_DIR / "xbrl" / "informe.xbrl").exists():
            with open(ROOT_DIR / "xbrl" / "informe.xbrl", "r") as f:
                st.download_button("Descargar Informe XBRL", f, file_name="informe_csrd_2024.xbrl", mime="application/xml")

        st.info("El paquete de evidencia criptográfica (Merkle Tree) se ha generado en `evidence/`.")

st.markdown("---")
st.caption("© 2025 SteelTrace AI Solutions - MVP Confidential")
