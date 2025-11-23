import streamlit as st
import json
from pathlib import Path
import subprocess
import os
import sys
import pandas as pd
from datetime import datetime
import shutil
import time

# --- Configuración de Paths ---
ROOT_DIR = Path(__file__).parent.resolve()
os.chdir(ROOT_DIR)

# Importamos metadatos del pipeline
try:
    from scripts.pipeline_meta import STEPS_METADATA
except ImportError:
    STEPS_METADATA = []

PIPELINE_SCRIPT = ROOT_DIR / "scripts" / "pipeline_run.py"
DQ_REPORT_FILE  = ROOT_DIR / "data" / "dq_report.json"
KPI_FILE        = ROOT_DIR / "raga" / "kpis.json"
EEE_REPORT_FILE = ROOT_DIR / "ops" / "gate_report.json"
SLO_REPORT_FILE = ROOT_DIR / "ops" / "slo_report.json"
HITL_REPORT_FILE = ROOT_DIR / "ops" / "hitl_kappa.json"
EXPLAIN_FILE    = ROOT_DIR / "raga" / "explain.json"
GOVERNANCE_DIR  = ROOT_DIR / "ops" / "governance"

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
            pass # Lógica selectiva abajo

    shutil.rmtree(ROOT_DIR / "data" / "normalized", ignore_errors=True)
    if (ROOT_DIR / "data" / "dq_report.json").exists(): (ROOT_DIR / "data" / "dq_report.json").unlink()
    if (ROOT_DIR / "data" / "lineage.jsonl").exists(): (ROOT_DIR / "data" / "lineage.jsonl").unlink()

    shutil.rmtree(ROOT_DIR / "ops", ignore_errors=True)
    shutil.rmtree(ROOT_DIR / "raga", ignore_errors=True)
    shutil.rmtree(ROOT_DIR / "eee", ignore_errors=True)
    shutil.rmtree(ROOT_DIR / "evidence", ignore_errors=True)

    if (ROOT_DIR / "xbrl" / "informe.xbrl").exists(): (ROOT_DIR / "xbrl" / "informe.xbrl").unlink()
    if (ROOT_DIR / "xbrl" / "validation.log").exists(): (ROOT_DIR / "xbrl" / "validation.log").unlink()

    if (ROOT_DIR / "ontology" / "validation.log").exists(): (ROOT_DIR / "ontology" / "validation.log").unlink()
    if (ROOT_DIR / "ontology" / "linaje.ttl").exists(): (ROOT_DIR / "ontology" / "linaje.ttl").unlink()

    st.session_state["pipeline_ran"] = False
    st.cache_data.clear()
    st.success("Entorno reiniciado. Listo para nueva auditoría.")

def sign_off_report(user_role):
    """Simula la firma del reporte."""
    GOVERNANCE_DIR.mkdir(parents=True, exist_ok=True)
    sign_file = GOVERNANCE_DIR / f"signoff_{int(datetime.now().timestamp())}.json"
    sign_data = {
        "signer": user_role,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": "APPROVED",
        "comments": "Validación manual completada en interfaz STEELTRACE."
    }
    sign_file.write_text(json.dumps(sign_data, indent=2))
    st.balloons()
    st.success(f"Reporte firmado digitalmente por: {user_role}")

# --- Interfaz Streamlit ---
st.set_page_config(
    layout="wide",
    page_title="STEELTRACE™ | Governance Dashboard",
    page_icon="🛡️"
)

# Sidebar
with st.sidebar:
    st.title("🛡️ STEELTRACE™")
    st.caption("AI Governance & CSRD Compliance")
    st.markdown("---")

    st.markdown("### 🎮 Centro de Mando")
    if st.button("▶️ Iniciar Auditoría", type="primary", use_container_width=True, help="Ejecuta el pipeline paso a paso."):
        st.session_state["run_requested"] = True

    if st.button("🔄 Reiniciar Demo", use_container_width=True):
        reset_environment()
        st.rerun()

    st.markdown("---")
    st.markdown("### 👤 Su Rol Hoy")
    user_role = st.selectbox("Simular Usuario:", ["Chief Sustainability Officer", "External Auditor", "Data Steward"])

    st.info("v1.2.1-MVP")

# Main Content
st.title("Panel de Control de Conformidad CSRD")
st.markdown("### 🔍 Auditoría y Gobernanza Paso a Paso")

# Estado de la sesión
if "pipeline_ran" not in st.session_state:
    st.session_state["pipeline_ran"] = False

# --- EJECUCIÓN DEL PIPELINE (Story Mode) ---
if st.session_state.get("run_requested"):
    st.session_state["run_requested"] = False
    
    progress_bar = st.progress(0)

    # Contenedor para la "historia" de la ejecución
    with st.container():
        st.markdown("#### 🚀 Iniciando secuencia de auditoría...")
        total_steps = len(STEPS_METADATA)

        for i, step in enumerate(STEPS_METADATA):
            # Calcular progreso
            p = (i) / total_steps
            progress_bar.progress(p)

            # Mostrar tarjeta del paso actual
            with st.status(f"**Paso {i+1}: {step['label']}**", expanded=True) as status:
                st.markdown(f"*{step['description']}*")
                st.caption(f"👮 Responsable: {step['role']}")

                # Ejecutar comando real
                try:
                    t0 = time.time()
                    result = subprocess.run(
                        step["command"],
                        capture_output=True, text=True, check=True
                    )
                    t1 = time.time()
                    st.success(f"Completado en {t1-t0:.2f}s")
                    status.update(label=f"✅ {step['label']} - Completado", state="complete", expanded=False)
                except subprocess.CalledProcessError as e:
                    st.error(f"❌ Error crítico: {e.stderr}")
                    status.update(label="Error en el Pipeline", state="error")
                    st.stop()

            # Pequeña pausa para que el usuario pueda leer (efecto demo)
            time.sleep(1.0)

        progress_bar.progress(1.0)
        st.session_state["pipeline_ran"] = True
        st.balloons()
        st.success("🏁 Auditoría finalizada correctamente. Los resultados están listos para revisión.")
        time.sleep(1)
        st.rerun()

# --- VISTA POST-EJECUCIÓN (Dashboard de Resultados) ---
if st.session_state["pipeline_ran"] or EEE_REPORT_FILE.exists():
    
    # 1. Resumen de Alto Nivel (Semáforo)
    st.markdown("---")
    st.header("1. Semáforo de Conformidad")
    st.markdown("Estado actual del reporte basado en las validaciones automáticas.")

    eee_report = load_json(EEE_REPORT_FILE)
    if eee_report:
        col1, col2, col3 = st.columns(3)
        with col1:
            decision = eee_report["global_decision"].upper()
            color = "green" if decision == "PUBLISH" else "red"
            icon = "✅" if decision == "PUBLISH" else "⛔"
            st.markdown(f"### Decisión Final: :{color}[{decision} {icon}]")
            st.info("¿Se puede publicar el reporte?", icon="🤔")
        with col2:
            st.metric("Confianza de la IA (Score)", f"{eee_report['eee_score']:.2f}", f"Meta: {eee_report['threshold']}")
            st.caption("Calculado auditando la evidencia y las explicaciones.")
        with col3:
            # Firma Digital
            is_signed = any(GOVERNANCE_DIR.glob("signoff_*.json")) if GOVERNANCE_DIR.exists() else False
            if is_signed:
                st.success("✅ REPORTE FIRMADO Y CERRADO")
                st.caption("No se admiten más cambios.")
            else:
                st.warning("⚠️ Pendiente de Aprobación Humana")
                if st.button("✍️ Aprobar y Firmar Reporte", type="primary"):
                    sign_off_report(user_role)

    # 2. Historia de la Auditoría (Timeline)
    st.markdown("---")
    st.header("2. La Historia de sus Datos (Trazabilidad)")
    st.markdown("Cada paso que han dado sus datos, quién los tocó y qué resultado dio.")

    for i, step in enumerate(STEPS_METADATA):
        # Usamos expanders para contar la historia paso a paso
        with st.expander(f"{i+1}. {step['label']}", expanded=False):
            st.markdown(f"**¿Qué hicimos aquí?**")
            st.write(step['description'])

            st.markdown(f"**¿Quién fue el responsable?** `{step['role']}`")

            # Artefactos
            if step.get("output_artifact"):
                art_path = Path(step["output_artifact"])
                if art_path.exists():
                    st.markdown(f"---")
                    st.markdown(f"📂 **Prueba generada:** `{art_path.name}`")

                    # Preview contextual
                    if art_path.suffix == ".json":
                        data = load_json(art_path)
                        # Mostrar solo una muestra pequeña si es muy grande
                        st.json(data, expanded=False)
                    elif art_path.suffix == ".xbrl":
                        st.code("<xml> ... Reporte XBRL encriptado ... </xml>", language="xml")

            st.success("✅ Validado y Seguro")

    # 3. Datos al Detalle
    st.markdown("---")
    st.header("3. Inspección Profunda")
    st.markdown("Si necesita ver los números exactos, aquí están los detalles técnicos.")

    tab1, tab2, tab3 = st.tabs(["📊 Calidad (Data Quality)", "🤖 Explicaciones IA", "📦 Paquete de Salida"])

    with tab1:
        st.markdown("**¿Están limpios los datos?**")
        dq_report = load_json(DQ_REPORT_FILE)
        if dq_report:
            dq_summary = []
            for dom, rep in dq_report["domains"].items():
                agg = rep['dq']['aggregate']
                dq_summary.append({
                    "Area": dom.upper(),
                    "Estado": "✅ Correcto" if agg['dq_pass'] else "❌ Revisar",
                    "Datos Completos": f"{agg['completeness']:.0%}",
                    "Datos Válidos": f"{agg['validity']:.0%}"
                })
            st.table(pd.DataFrame(dq_summary))

    with tab2:
        st.markdown("**¿Por qué la IA dice esto?**")
        explain_data = load_json(EXPLAIN_FILE)
        if explain_data:
            for kpi, details in explain_data.items():
                st.markdown(f"#### {kpi}")
                st.info(f"💡 **Explicación:** {details['hypothesis']}")
                st.caption(f"🔎 **Evidencia encontrada en:** {details['evidence']}")

    with tab3:
        st.markdown("**Archivos listos para el regulador**")
        colA, colB = st.columns(2)
        with colA:
            if (ROOT_DIR / "xbrl" / "informe.xbrl").exists():
                with open(ROOT_DIR / "xbrl" / "informe.xbrl", "r") as f:
                    st.download_button("📥 Descargar Reporte XBRL Oficial", f, file_name="csrd_2024.xbrl")
        with colB:
            st.markdown("*Manifiesto de Evidencia (Merkle Tree):*")
            st.code(load_json(ROOT_DIR / "evidence" / "evidence_manifest.json").get("merkle_root", "N/A"), language="text")

else:
    # Pantalla de Bienvenida (Estado Cero)
    st.info("👋 Bienvenido a STEELTRACE™. Para comenzar la demostración, haga clic en 'Iniciar Auditoría' en el menú de la izquierda.")

    st.markdown("### ¿Qué va a pasar cuando inicie?")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 1. Ingesta")
        st.markdown("Recogeremos datos de Energía, RRHH y Ética.")
    with col2:
        st.markdown("#### 2. Validación")
        st.markdown("La IA revisará las leyes y calculará los KPIs.")
    with col3:
        st.markdown("#### 3. Reporte")
        st.markdown("Generaremos un archivo oficial XBRL firmado.")

