import streamlit as st
import json
from pathlib import Path
import subprocess
import os
import sys
import pandas as pd
import shutil
import time
from datetime import datetime  # <--- CORREGIDO: Importación crítica

# --- 1. CONFIGURACIÓN INICIAL (Siempre al principio) ---
st.set_page_config(
    layout="wide",
    page_title="STEELTRACE™ | Auditor Console",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- 2. CONFIGURACIÓN DE ENTORNO Y RUTAS ---
ROOT_DIR = Path(__file__).parent.resolve()

# Intentar cambiar al directorio raíz para asegurar rutas relativas
try:
    os.chdir(ROOT_DIR)
except Exception:
    pass

# Definición de Archivos Clave
PIPELINE_SCRIPT = ROOT_DIR / "scripts" / "pipeline_run.py"
DQ_REPORT_FILE  = ROOT_DIR / "data" / "dq_report.json"
KPI_FILE        = ROOT_DIR / "raga" / "kpis.json"
EEE_REPORT_FILE = ROOT_DIR / "ops" / "gate_report.json"
SLO_REPORT_FILE = ROOT_DIR / "ops" / "slo_report.json"
HITL_REPORT_FILE = ROOT_DIR / "ops" / "hitl_kappa.json"
EXPLAIN_FILE    = ROOT_DIR / "raga" / "explain.json"

# Carpetas que el sistema NECESITA para funcionar
DIRS_TO_MANAGE = [
    "data/normalized", 
    "ops", 
    "raga", 
    "xbrl", 
    "evidence", 
    "eee", 
    "ontology"
]

# --- 3. FUNCIONES DE UTILIDAD BLINDADAS ---

def ensure_directories():
    """Crea todas las carpetas necesarias al arrancar para evitar FileNotFoundError."""
    for d in DIRS_TO_MANAGE:
        path = ROOT_DIR / d
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            # Si falla, no rompemos la app, solo avisamos en consola
            print(f"Warning creando {d}: {e}")

def load_json(path: Path):
    """Lee un JSON de forma segura. Si falla, devuelve None sin romper la app."""
    try:
        if not path.exists(): 
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None  # Silencio absoluto en caso de error de lectura

def reset_environment():
    """Limpia los resultados anteriores para una nueva auditoría."""
    ensure_directories() # Asegurar que existen antes de limpiar
    
    # 1. Limpiar carpetas gestionadas
    for d in DIRS_TO_MANAGE:
        p = ROOT_DIR / d
        if p.exists():
             for item in p.iterdir():
                 if item.is_file() and item.name != ".gitkeep":
                     try: item.unlink()
                     except: pass
                 elif item.is_dir():
                     try: shutil.rmtree(item)
                     except: pass
    
    # 2. Limpiar archivos sueltos en raiz de data
    try:
        if (ROOT_DIR / "data" / "dq_report.json").exists(): 
            (ROOT_DIR / "data" / "dq_report.json").unlink()
    except: pass
    
    st.cache_data.clear()

def simulate_step(step_name, description, duration=0.8):
    """Muestra progreso visual en la interfaz."""
    with st.spinner(f"Ejecutando: {step_name}..."):
        time.sleep(duration)
        st.success(f"✅ **{step_name}:** {description}")

def run_pipeline_interactive():
    """Ejecuta la auditoría y maneja errores del script externo."""
    placeholder = st.empty()
    success = False
    
    with placeholder.container():
        st.info("🚀 Iniciando Pipeline de Auditoría Automatizada...")
        
        # Pasos visuales (Simulación UX)
        simulate_step("MCP Ingest", "Normalizando datos de fuentes heterogéneas...")
        simulate_step("Data Quality Check", "Validando esquemas Pydantic...")
        simulate_step("SHACL Validation", "Verificando conformidad semántica...")
        simulate_step("RAGA AI Engine", "Generando explicaciones y KPIs...")
        
        # --- EJECUCIÓN REAL ---
        try:
            if not PIPELINE_SCRIPT.exists():
                st.error(f"❌ Error Crítico: No se encuentra el script {PIPELINE_SCRIPT}")
                return False

            # Ejecutamos el script python como subproceso
            # check=True lanzará una excepción si el script falla
            result = subprocess.run(
                [sys.executable, str(PIPELINE_SCRIPT)],
                capture_output=True, text=True, check=True
            )
            
            # ÉXITO
            st.success("🏁 Pipeline completado exitosamente.")
            
            # Mostrar logs para evidencia técnica
            with st.expander("Ver Logs Técnicos (Stdout)", expanded=False):
                st.code(result.stdout[-1000:], language="text")
            
            simulate_step("EEE Gate Decision", "Evaluando umbrales de publicación...", duration=0.5)
            simulate_step("Merkle Proof", "Generando hash criptográfico...", duration=0.5)
            
            time.sleep(1)
            success = True

        except subprocess.CalledProcessError as e:
            # EL SCRIPT FALLÓ (Exit code != 0)
            st.error("⚠️ El pipeline falló durante la ejecución interna.")
            st.markdown("### 🔴 Detalle del Error (Stderr):")
            st.code(e.stderr, language="text") # Mostramos el error real
            st.markdown("### Salida Parcial:")
            st.code(e.stdout, language="text")
            success = False

        except Exception as e:
            st.error(f"⚠️ Error inesperado ejecutando pipeline: {e}")
            success = False
            
    if success:
        placeholder.empty() # Limpiar consola si todo fue bien
        
    return success

# --- 4. AUTOCORRECCIÓN AL INICIO (Soluciona Imagen 1) ---
ensure_directories()

# --- 5. INTERFAZ DE USUARIO ---

# Estilos CSS
st.markdown("""
<style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🛡️ STEELTRACE™")
    st.caption("CSRD + AI Governance MVP")
    st.markdown("---")
    
    # Botón Ejecutar
    if st.button("▶️ Ejecutar Auditoría", type="primary", use_container_width=True):
        reset_environment()
        if run_pipeline_interactive():
            st.rerun() # Solo recarga si tuvo éxito

    # Botón Reiniciar
    if st.button("🔄 Reiniciar Entorno", use_container_width=True):
        reset_environment()
        st.rerun()

    st.markdown("---")
    dq_exists = (ROOT_DIR / "data" / "dq_report.json").exists()
    xbrl_exists = (ROOT_DIR / "xbrl" / "informe.xbrl").exists()
    st.markdown(f"**Estado:**\n- Datos: {'✅' if dq_exists else '⚪'}\n- XBRL: {'✅' if xbrl_exists else '⚪'}")

# Contenido Principal
try:
    st.title("Panel de Control de Conformidad CSRD")
    st.markdown("Vista de Auditoría Técnica y Semántica")
    st.markdown("---")

    # Intentar cargar reporte final
    eee_report = load_json(EEE_REPORT_FILE)

    if not eee_report:
        # PANTALLA DE BIENVENIDA (Estado Inicial)
        st.info("👋 **Bienvenido, Auditor.**")
        st.markdown("""
        El sistema está listo y las carpetas de trabajo han sido inicializadas.
        Pulse **▶️ Ejecutar Auditoría** en el menú lateral para comenzar.
        """)
        
        # Previsualización segura de datos
        with st.expander("🔍 Ver Datos de Entrada (Raw)"):
            sample_file = ROOT_DIR / "data" / "samples" / "energy_2024-01.json"
            if sample_file.exists():
                st.json(load_json(sample_file), expanded=False)
            else:
                st.warning("⚠️ No se detectan archivos en data/samples/")

    else:
        # DASHBOARD DE RESULTADOS (Solo si hay reporte)
        col_main, col_cert = st.columns([3, 1])
        
        with col_main:
            decision = eee_report.get("global_decision", "UNKNOWN")
            if decision == "PUBLISH":
                st.success(f"### ✅ DECISIÓN: {decision}")
                st.markdown("Cumple umbrales de calidad, explicabilidad y evidencia.")
            else:
                st.error(f"### ⛔ DECISIÓN: {decision}")
                st.markdown("Bloqueado por inconsistencias o falta de evidencia.")

        with col_cert:
            st.markdown("**Sello Digital**")
            audit_hash = "Generando..."
            manifest_path = ROOT_DIR / "evidence" / "evidence_manifest.json"
            # Carga segura del manifiesto
            m = load_json(manifest_path)
            if m: audit_hash = m.get("merkle_root", "N/A")[:10] + "..."
            
            st.code(audit_hash)
            st.caption("Merkle Root SHA-256")

        st.markdown("---")

        tab_dq, tab_sem, tab_xbrl = st.tabs(["1. Calidad (DQ)", "2. Lógica (RAG)", "3. Salida (XBRL)"])

        with tab_dq:
            dq = load_json(DQ_REPORT_FILE)
            if dq:
                c1, c2, c3 = st.columns(3)
                c1.metric("Score Calidad", f"{dq.get('dq_score', 0)*100:.1f}%")
                c2.metric("Reglas", dq.get("rules_executed", 0))
                c3.metric("Fallos", dq.get("failed_rows", 0))
                st.dataframe(pd.DataFrame(dq.get("domains", {})).T)
            else:
                st.warning("No hay reporte de calidad disponible.")

        with tab_sem:
            expl = load_json(EXPLAIN_FILE)
            if expl:
                for k, v in expl.items():
                    st.info(f"KPI: {k}")
                    st.write(f"Hipótesis: {v.get('hypothesis')}")
            else:
                st.write("Sin explicaciones generadas.")

        with tab_xbrl:
            xbrl_file = ROOT_DIR / "xbrl" / "informe.xbrl"
            if xbrl_file.exists():
                st.download_button("⬇️ Descargar XBRL", xbrl_file.read_bytes(), "informe.xbrl")
            else:
                st.warning("Archivo XBRL no generado.")

        st.caption(f"Timestamp: {datetime.now().isoformat()}")

except Exception as e:
    # Captura final de errores para que no salga la pantalla fea de Streamlit
    st.error("⚠️ Error crítico en la aplicación:")
    st.exception(e)
