from __future__ import annotations

import streamlit as st

from app_utils import DEFAULTS, PATHS, load_json, load_text

st.title("EEE Gate")
st.caption("Filtro Epistemic–Explicit–Evidence antes de publicar")

report = load_json(PATHS["gate"], DEFAULTS["gate"])
cfg_text = load_text(PATHS["eee_cfg"], "Sin ops/eee_gate.yaml todavía")

st.markdown(
    """
    El gate combina tres componentes para decidir si un KPI puede publicarse:

    * **Epistemic**: confianza en el residuo del modelo (`residual`).
    * **Explicit**: presencia de hipótesis, evidencias y citas por dato publicado.
    * **Evidence**: existencia de artefactos obligatorios (RAGA, SHACL, etc.).
    """
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("EEE score", report.get("eee_score", 0.0))
with col2:
    st.metric("Umbral", report.get("threshold", 0.0))
with col3:
    st.metric("Decisión global", report.get("global_decision", "-"))

st.write("### Peso por componente")
components = report.get("components", {})
st.bar_chart(
    {
        "Epistemic": [components.get("epistemic", 0)],
        "Explicit": [components.get("explicit", 0)],
        "Evidence": [components.get("evidence", 0)],
    }
)

with st.expander("Detalle por Data Point"):
    for detail in report.get("details", []):
        st.write(detail.get("dp", ""))
        st.json(detail)

st.markdown("---")

st.write("### Configuración aplicada")
st.code(cfg_text, language="yaml")

st.info("El gate deja trazabilidad en `ops/gate_report.json` y `eee/eee_report.json`. Estos archivos se incluyen en el manifiesto de evidencias.")
