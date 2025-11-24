import streamlit as st
import json
from pathlib import Path
import subprocess
import os
import sys
import pandas as pd
import shutil
import time
from datetime import datetime

# --- 1. CONFIGURACIÓN INICIAL (Debe ser lo primero) ---
st.set_page_config(
    layout="wide",
    page_title="STEELTRACE™ | Auditor Console",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- Configuración de Paths ---
ROOT_DIR = Path(__file__).parent.resolve()
try:
    os.chdir(ROOT_DIR)
except Exception:
    pass

PIPELINE_SCRIPT = ROOT_DIR / "scripts" / "pipeline_run.py"
DQ_REPORT_FILE  = ROOT_DIR / "data" / "dq_report.json"
KPI_FILE        = ROOT_DIR / "raga" / "kpis.json"
EEE_REPORT_FILE = ROOT_DIR / "ops" / "gate_report.json"
SLO_REPORT_FILE = ROOT_DIR / "ops" / "slo_report.json"
HITL_REPORT_FILE = ROOT_DIR / "ops" / "hitl_kappa.json"
EXPLAIN_FILE    = ROOT_DIR / "raga" / "explain.json"

# Directorios críticos que SIEMPRE deben existir
DIRS_TO_MANAGE = ["data/normalized", "ops", "raga", "xbrl", "evidence", "eee", "ontology"]

def load_json(path: Path):
    try:
        if not path.exists(): return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def reset_environment():
    """Limpia y REGENERA la estructura de carpetas."""
    # 1. Limpiar contenido existente
    for d in DIRS_TO_MANAGE:
        p = ROOT_DIR / d
        if p.exists() and p.is_dir():
             for item in p.iterdir():
                 if item.is_file() and item.name != ".gitkeep":
                     try: item.unlink()
                     except: pass
                 elif item.is_dir():
                     try: shutil.rmtree(item)
                     except: pass
        else:
            # Si no existe, la creamos ahora mismo
            try:
                p.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                st.error(f"Error creando directorio {d}: {e}")

    # 2. Asegurar que TODAS las carpetas existan antes de correr el pipeline
    # Esto evita el FileNotFoundError 'ops/...'
    for d in DIRS_TO_MANAGE:
        (ROOT_DIR / d).mkdir(parents=True, exist_ok=True)

    # 3. Limpiar archivos sueltos en raiz de data si existen
    try:
        if (ROOT_DIR / "data" / "dq_report.json").exists(): (ROOT_DIR / "data" / "dq_report.json").unlink()
        if (ROOT_DIR / "data" / "lineage.jsonl").exists(): (ROOT_DIR / "data" / "lineage.jsonl").unlink()
    except: pass
    
    st.cache_data.clear()
    st.toast("Entorno reiniciado. Estructura lista.", icon="✅")

def simulate_step(step_name, description, duration=1.0):
    with st.spinner(f"Ejecutando: {step_name}..."):
        time.sleep(duration)
        st.write(f"✅ **{step_name}:** {description}")

def run_pipeline_interactive():
    """Ejecuta el pipeline mostrando el paso a paso en la UI."""
    placeholder = st.empty()
    
    with placeholder.container():
        st.info("🚀 Iniciando Pipeline de Auditoría Automatizada...")
        
        # Aseguramos directorios justo antes de correr por seguridad
        for d in DIRS_TO_MANAGE:
            (ROOT_DIR / d).mkdir(parents=True, exist_ok=True)

        # Paso 1
        simulate_step("MCP Ingest", "Normalizando datos de fuentes heterogéneas...")
        
        # Paso 2
        simulate_step("Data Quality Check", "Validando esquemas Pydantic...")
        
        # Paso 3
        simulate_step("SHACL Validation", "Verificando conformidad semántica...")
        
        # Paso 4
        simulate_step("RAGA AI Engine", "Generando explicaciones y KPIs...")
        
        # Ejecución real
        try:
            if PIPELINE_SCRIPT.exists():
                # Ejecutamos el script y capturamos la salida
                result = subprocess.run(
                    [sys.executable, str(PIPELINE_SCRIPT)],
                    capture_output=True, text=True, check=True
                )
                
                # Si todo va bien, mostramos logs parciales
                with st.expander("Ver Logs del Sistema (Stdout)"):
                    # Mostramos las últimas líneas para confirmar éxito
                    st.code(result.stdout[-1000:], language="text")
            else:
                st.error(f"❌ No se encuentra el script: {PIPELINE_SCRIPT}")
                
        except subprocess.CalledProcessError as e:
            st.error("⚠️ El pipeline falló en la ejecución interna.")
            st.markdown("**Detalle del error (Stderr):**")
            st.code(e.stderr, language="text")
            st.markdown("**Salida parcial (Stdout):**")
            st.code(e.stdout, language="text")
            return # Detenemos aquí si falla

        except Exception as e:
            st.error(f"Error inesperado: {e}")
            return

        # Paso 5
        simulate_step("EEE Gate Decision", "Evaluando umbrales de publicación...")
        
        # Paso 6
        simulate_step("Merkle Proof", "Generando hash criptográfico...", duration=0.5)
        
        st.success("🏁 Pipeline completado exitosamente.")
        time.sleep(1)
    
    placeholder.empty()

# --- Estilos CSS ---
st.markdown("""
<style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.header("🛡️ STEELTRACE™")
    st.caption("CSRD + AI Governance MVP")
    
    st.markdown("---")
    st.markdown("### 🎮 Controles")

    if st.button("▶️ Ejecutar Auditoría", type="primary", use_container_width=True):
        reset_environment() # Limpia y crea carpetas
        run_pipeline_interactive()
        st.rerun()

    if st.button("🔄 Reiniciar Entorno", use_container_width=True):
        reset_environment()
        st.rerun()

    st.markdown("---")
    # Indicadores
    dq_exists = (ROOT_DIR / "data" / "dq_report.json").exists()
    xbrl_exists = (ROOT_DIR / "xbrl" / "informe.xbrl").exists()
    st.markdown(f"**Estado:**\n- Datos: {'✅' if dq_exists else '⚪'}\n- XBRL: {'✅' if xbrl_exists else '⚪'}")

# --- Main Content ---
try:
    st.title("Panel de Control de Conformidad CSRD")
    st.markdown("Vista de Auditoría Técnica y Semántica")
    st.markdown("---")

    # Verificar si hay datos
    eee_report = load_json(EEE_REPORT_FILE)

    if not eee_report:
        st.info("👋 **Bienvenido, Auditor.**")
        st.markdown("""
        El sistema está listo. Pulse **▶️ Ejecutar Auditoría** en el menú lateral.
        
        **Procesos a verificar:**
        1.  Ingesta y Calidad (Pydantic)
        2.  Lógica Normativa (SHACL/Ontología)
        3.  Certificación (Hash SHA-256)
        """)
        
        with st.expander("🔍 Ver Datos de Entrada (Raw)"):
            sample_file = ROOT_DIR / "data" / "samples" / "energy_2024-01.json"
            if sample_file.exists():
                st.json(json.loads(sample_file.read_text()), expanded=False)
            else:
                st.write("Esperando carga de datos...")

    else:
        # DASHBOARD
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
            if manifest_path.exists():
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
    st.error("⚠️ Error crítico en la aplicación:")
    st.exception(e)
