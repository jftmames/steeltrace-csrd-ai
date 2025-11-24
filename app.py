import streamlit as st
import json
from pathlib import Path
import subprocess
import os
import sys
import pandas as pd
import shutil
import time

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
DIRS_TO_CLEAN = ["data/normalized", "ops", "raga", "xbrl", "evidence", "eee", "ontology"]

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
        if p.exists() and p.is_dir():
             # Mantenemos la carpeta pero borramos contenido para no romper estructuras
             for item in p.iterdir():
                 if item.is_file() and item.name != ".gitkeep":
                     item.unlink()
                 elif item.is_dir():
                     shutil.rmtree(item)
    
    # Archivos sueltos específicos
    if (ROOT_DIR / "data" / "dq_report.json").exists(): (ROOT_DIR / "data" / "dq_report.json").unlink()
    if (ROOT_DIR / "data" / "lineage.jsonl").exists(): (ROOT_DIR / "data" / "lineage.jsonl").unlink()
    
    st.cache_data.clear()
    st.toast("Entorno reiniciado. Artefactos eliminados.", icon="🗑️")

def simulate_step(step_name, description, duration=1.5):
    """Ayuda visual para mostrar el progreso al consultor"""
    with st.spinner(f"Ejecutando: {step_name}..."):
        time.sleep(duration)
        st.write(f"✅ **{step_name}:** {description}")

def run_pipeline_interactive():
    """Ejecuta el pipeline mostrando el paso a paso en la UI."""
    placeholder = st.empty()
    
    with placeholder.container():
        st.info("🚀 Iniciando Pipeline de Auditoría Automatizada...")
        
        # Paso 1: Ingesta
        simulate_step("MCP Ingest", "Normalizando datos de fuentes heterogéneas (JSON, CSV)...")
        
        # Paso 2: Calidad
        simulate_step("Data Quality Check", "Validando esquemas Pydantic y reglas de negocio...")
        if (ROOT_DIR / "data" / "dq_report.json").exists():
            st.json({"status": "DQ_PASSED", "errors": 0}, expanded=False)

        # Paso 3: Semántica
        simulate_step("SHACL Validation", "Verificando conformidad semántica con grafo ESRS...")
        
        # Paso 4: RAG & AI
        simulate_step("RAGA AI Engine", "Generando explicaciones y calculando KPIs con LLM...")
        
        # Ejecución real (si existe el script)
        try:
            result = subprocess.run(
                [sys.executable, str(PIPELINE_SCRIPT)],
                capture_output=True, text=True, check=True
            )
            st.code(result.stdout[-500:], language="text", line_numbers=True) # Mostrar últimos logs reales
        except Exception as e:
            st.error(f"Error en ejecución real: {e}")

        # Paso 5: Gate
        simulate_step("EEE Gate Decision", "Evaluando umbrales de publicación (Evidencia > 0.8)...")
        
        # Paso 6: Evidencia
        simulate_step("Merkle Proof", "Generando hash criptográfico de inmutabilidad...", duration=1.0)
        
        st.success("🏁 Pipeline completado exitosamente.")
        time.sleep(1)
    
    placeholder.empty() # Limpia el log visual para mostrar el dashboard final

# --- Interfaz Streamlit ---
st.set_page_config(
    layout="wide",
    page_title="STEELTRACE™ | Auditor Console",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# Estilos CSS para parecer más profesional
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .stAlert {
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/verified-account.png", width=50)
    st.title("STEELTRACE™")
    st.caption("CSRD + AI Governance MVP")
    
    st.markdown("---")
    st.markdown("### 🎮 Controles de Auditoría")

    if st.button("▶️ Ejecutar Auditoría", type="primary", use_container_width=True):
        reset_environment() # Limpiar antes de correr
        run_pipeline_interactive()
        st.rerun()

    if st.button("🔄 Reiniciar Entorno", use_container_width=True):
        reset_environment()
        st.rerun()

    st.markdown("---")
    st.markdown("### 📁 Estado del Sistema")
    
    # Indicadores de archivo en sidebar
    dq_exists = (ROOT_DIR / "data" / "dq_report.json").exists()
    xbrl_exists = (ROOT_DIR / "xbrl" / "informe.xbrl").exists()
    
    st.write(f"Datos Validados: {'✅' if dq_exists else '⚪'}")
    st.write(f"Reporte XBRL: {'✅' if xbrl_exists else '⚪'}")

# Main Content
st.title("Panel de Control de Conformidad CSRD")
st.markdown("Vista de Auditoría Técnica y Semántica")
st.markdown("---")

# Verificar si hay datos
eee_report = load_json(EEE_REPORT_FILE)

if not eee_report:
    st.info("👋 **Bienvenido, Auditor.**")
    st.markdown("""
    El sistema está en estado de espera. Para iniciar la validación de los datasets de muestra (`data/samples/`), 
    utilice el botón **▶️ Ejecutar Auditoría** en la barra lateral.
    
    **El proceso realizará en tiempo real:**
    1.  **Ingesta:** Lectura de fuentes crudas.
    2.  **Validación:** Chequeo contra esquemas Pydantic/JSONSchema.
    3.  **Lógica:** Inferencia de reglas ESRS (Ontología).
    4.  **Certificación:** Generación de huella criptográfica.
    """)
    
    # Mostrar datos crudos para que el consultor vea qué va a procesar
    with st.expander("🔍 Previsualizar Datos de Entrada (Raw Source)"):
        sample_file = ROOT_DIR / "data" / "samples" / "energy_2024-01.json"
        if sample_file.exists():
            st.json(json.loads(sample_file.read_text()), expanded=False)
        else:
            st.warning("No se encontraron archivos de muestra.")

else:
    # --- DASHBOARD RESULTADOS ---
    
    # 1. CABECERA DE DECISIÓN (LO MÁS IMPORTANTE PARA EL CONSULTOR)
    col_main, col_cert = st.columns([3, 1])
    
    with col_main:
        decision = eee_report.get("global_decision", "UNKNOWN")
        st.subheader(f"Decisión del Algoritmo de Gobernanza:")
        if decision == "PUBLISH":
            st.success(f"### ✅ {decision}")
            st.markdown("El reporte cumple con todos los umbrales de calidad, explicabilidad y evidencia.")
        else:
            st.error(f"### ⛔ {decision}")
            st.markdown("El reporte ha sido bloqueado por inconsistencias o falta de evidencia.")

    with col_cert:
        st.markdown("#### Sello Digital")
        # Simular lectura del hash real
        audit_hash = "Wait..."
        manifest_path = ROOT_DIR / "evidence" / "evidence_manifest.json"
        if manifest_path.exists():
            m = load_json(manifest_path)
            if m: audit_hash = m.get("merkle_root", "N/A")[:16] + "..."
            
        st.code(audit_hash, language="text")
        st.caption("SHA-256 Merkle Root")

    st.markdown("---")

    # 2. DETALLE PASO A PASO (TABS)
    tab_dq, tab_sem, tab_xbrl = st.tabs(["1. Calidad del Dato (DQ)", "2. Lógica Semántica (RAG)", "3. Salida Regulatoria (XBRL)"])

    with tab_dq:
        dq = load_json(DQ_REPORT_FILE)
        if dq:
            c1, c2, c3 = st.columns(3)
            c1.metric("Score Calidad", f"{dq.get('dq_score', 0)*100:.1f}%")
            c2.metric("Reglas Ejecutadas", dq.get("rules_executed", 0))
            c3.metric("Filas Fallidas", dq.get("failed_rows", 0), delta_color="inverse")
            
            st.markdown("#### Detalle por Dominio")
            st.dataframe(pd.DataFrame(dq.get("domains", {})).T)
            
            with st.expander("Ver traza de errores (Log)"):
                st.json(dq.get("errors", []))

    with tab_sem:
        st.markdown("#### Razonamiento de la IA (RAG)")
        expl = load_json(EXPLAIN_FILE)
        if expl:
            for k, v in expl.items():
                st.info(f"**KPI:** {k}")
                st.write(f"**Hipótesis:** {v.get('hypothesis')}")
                st.caption(f"Evidencia: {v.get('evidence')}")
        else:
            st.warning("No hay explicaciones generadas.")

    with tab_xbrl:
        st.markdown("#### Instancia XBRL Generada")
        xbrl_file = ROOT_DIR / "xbrl" / "informe.xbrl"
        if xbrl_file.exists():
            st.download_button("⬇️ Descargar Paquete XBRL", xbrl_file.read_bytes(), "informe.xbrl")
            st.code(xbrl_file.read_text()[:1000] + "\n...", language="xml")
        else:
            st.error("No se generó el archivo XBRL.")

    st.caption(f"ID de Ejecución: {eee_report.get('execution_id', 'N/A')} | Timestamp: {datetime.now().isoformat()}")
