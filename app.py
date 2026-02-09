from __future__ import annotations

import streamlit as st

from app_utils import DEFAULTS, PATHS, ensure_dirs, load_json, run_full_pipeline

st.set_page_config(
    layout="wide",
    page_title="STEELTRACE™ | Auditoría CSRD paso a paso",
    page_icon="🛡️",
    initial_sidebar_state="expanded",
)

ensure_dirs()

# Cargamos artefactos ya generados o usamos respaldos para que la UI nunca quede vacía
report = load_json(PATHS["gate"], DEFAULTS["gate"])
dq = load_json(PATHS["dq"], DEFAULTS["dq"])
manifest = load_json(PATHS["manifest"], DEFAULTS["manifest"])

with st.sidebar:
    st.header("Orquestador")
    if st.button("▶️ Ejecutar pipeline completo", use_container_width=True):
        with st.spinner("Corriendo scripts/mcp_ingest.py → evidence_build.py..."):
            result = run_full_pipeline()
        st.session_state["last_run"] = result
        st.success(
            f"Pipeline {'OK' if result['ok'] else 'con errores'} en {result['elapsed']:.2f}s"
        )
        if result["stderr"]:
            st.caption(result["stderr"])

    st.markdown("---")
    st.subheader("Estado rápido")
    st.metric("EEE score", f"{report.get('eee_score', 0):.2f}")
    st.metric("Decisión", report.get("global_decision", "-"))
    st.metric("Hash raíz", manifest.get("merkle_root", "N/A")[:12] + "...")

    st.markdown("---")
    st.caption(
        "Esta barra te permite disparar el pipeline end-to-end y observar artefactos en las páginas específicas."
    )

st.title("CSRD+AI dividido en mini-aplicaciones")
st.markdown(
    """
    Para mostrar la complejidad de cada fase, el MVP ahora está dividido en páginas independientes.
    Cada una explica **qué hace** el agente, qué entradas consume y qué artefactos entrega.
    """
)

col1, col2, col3 = st.columns(3)
with col1:
    st.success("**EEE gate**\n# {0:.2f}".format(report.get("eee_score", 0)))
with col2:
    dq_domains = dq.get("domains", {})
    st.info(f"**Dominios DQ**\n# {len(dq_domains) if isinstance(dq_domains, dict) else 0}")
with col3:
    st.warning(f"**Merkle Root**\n# {manifest.get('merkle_root', 'N/A')[:10]}...")

st.markdown("---")

st.write("### Cómo navegar")
st.markdown(
    """
    1. **MCP.ingest + Data Quality**: normaliza datos crudos y aplica reglas DQ.
    2. **SHACL & Linaje RDF**: mapea los JSON a RDF y valida contra ontologías ESRS.
    3. **RAGA (KPIs + Explicaciones)**: calcula métricas y enlaza citas normativas.
    4. **EEE Gate**: aplica el filtro Epistemic–Explicit–Evidence.
    5. **XBRL**: serializa el informe digital y registra el log de validación.
    6. **Evidencias y Merkle**: resume artefactos firmados y linaje.
    """
)

st.info(
    "En cada pestaña encontrarás ejemplos completos (entradas, salidas y cálculos intermedios) para inspeccionar paso a paso."
)

if "last_run" in st.session_state:
    lr = st.session_state["last_run"]
    st.markdown("---")
    st.write("### Última ejecución manual")
    st.json({"ok": lr.get("ok"), "elapsed": lr.get("elapsed"), "stderr": lr.get("stderr", "")})
    if lr.get("stdout"):
        with st.expander("Ver stdout del pipeline"):
            st.code(lr["stdout"], language="bash")
