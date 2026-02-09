from __future__ import annotations

import streamlit as st

from app_utils import DEFAULTS, PATHS, load_json

st.title("RAGA: KPIs + Explicaciones")
st.caption("Cálculo de métricas y grounding normativo")

st.markdown(
    """
    El agente **RAGA.compute** consume los JSON normalizados para calcular KPIs regulatorios
    y adjuntar explicaciones trazables:

    1. Calcula **E1-1 CO2e**, **S1-1 rotación** y **G1-1 resolución**.
    2. Para cada KPI almacena hipótesis, evidencia y citas a la norma ESRS.
    3. Guarda `raga/kpis.json` y `raga/explain.json` para las etapas siguientes.
    """
)

kpis = load_json(PATHS["kpis"], DEFAULTS["kpis"])
explain = load_json(PATHS["explain"], DEFAULTS["explain"])

if not kpis:
    st.warning("Aún no hay KPIs calculados. Ejecuta el pipeline desde la página principal.")

for kpi_id, value in kpis.items():
    st.subheader(kpi_id)
    st.metric("Valor", value)
    exp = explain.get(kpi_id, {}) if isinstance(explain, dict) else {}
    st.write("**Hipótesis**", exp.get("hypothesis", "-"))
    st.write("**Evidencias**")
    st.code("\n".join(exp.get("evidence", [])), language="text")
    st.write("**Citas normativas**")
    st.json(exp.get("citations", []))

st.markdown("---")

st.write("### Artefactos producidos")
col1, col2 = st.columns(2)
with col1:
    st.write("`raga/kpis.json`")
    st.json(kpis)
with col2:
    st.write("`raga/explain.json`")
    st.json(explain)

st.info("Las explicaciones alimentan el gate EEE y la generación de reportes para auditores.")
