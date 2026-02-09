from __future__ import annotations

import streamlit as st

from app_utils import DEFAULTS, PATHS, ROOT_DIR, load_json

st.title("MCP.ingest + Data Quality")
st.caption("Normalización y control de calidad de datos crudos")

st.markdown(
    """
    Esta mini-app muestra el agente de ingesta funcionando en tres dominios (E1, S1, G1):

    1. **Carga y validación JSON Schema** por dominio.
    2. **Normalización** y escritura de `data/normalized/*.json`.
    3. **Reglas DQ** (completitud, validez, consistencia y oportunidad) con resultado detallado.
    """
)

dq_report = load_json(PATHS["dq"], DEFAULTS["dq"])
raw_energy = load_json(ROOT_DIR / "data" / "samples" / "energy_2024-01.json", [])
raw_hr = load_json(ROOT_DIR / "data" / "samples" / "hr_2024-01.json", [])
raw_ethics = load_json(ROOT_DIR / "data" / "samples" / "ethics_2024-01.json", [])

norm_energy = load_json(ROOT_DIR / "data" / "normalized" / "energy_2024-01.json", [])
norm_hr = load_json(ROOT_DIR / "data" / "normalized" / "hr_2024-01.json", [])
norm_ethics = load_json(ROOT_DIR / "data" / "normalized" / "ethics_2024-01.json", [])

col1, col2, col3 = st.columns(3)
for col, name, sample, normalized in [
    (col1, "E1 | Energía", raw_energy, norm_energy),
    (col2, "S1 | Personas", raw_hr, norm_hr),
    (col3, "G1 | Ética", raw_ethics, norm_ethics),
]:
    with col:
        st.subheader(name)
        st.metric("Registros crudos", len(sample) if isinstance(sample, list) else 0)
        st.metric("Normalizados", len(normalized) if isinstance(normalized, list) else 0)
        st.caption("Se valida contra contratos JSON en `contracts/`.")

st.markdown("---")

st.write("### Ejemplo de transformación")
with st.expander("Ver energéticos crudos → normalizados"):
    st.json({"raw": raw_energy, "normalized": norm_energy})
with st.expander("Ver RRHH crudos → normalizados"):
    st.json({"raw": raw_hr, "normalized": norm_hr})
with st.expander("Ver Ética crudos → normalizados"):
    st.json({"raw": raw_ethics, "normalized": norm_ethics})

st.markdown("---")

st.write("### Reglas de calidad ejecutadas")
domains = dq_report.get("domains", {})
for domain, payload in domains.items():
    st.subheader(f"Dominio {domain}")
    dq_meta = payload.get("dq", {})
    agg = dq_meta.get("aggregate", {})
    st.metric("Score DQ", f"{agg.get('completeness', 0)*100:.0f}% completitud")
    cols = st.columns(4)
    for c, key in zip(cols, ["completeness", "validity", "consistency", "timeliness"]):
        c.metric(key.capitalize(), f"{agg.get(key, 0)*100:.0f}%")

    with st.expander("Detalle de reglas y tasas de pase"):
        for category, rules in dq_meta.get("by_rule", {}).items():
            st.write(f"**{category.capitalize()}**")
            rows = [
                {
                    "rule": r.get("rule", {}).get("rule", ""),
                    "field": r.get("rule", {}).get("field", "-"),
                    "pass_rate": round(r.get("pass_rate", 0) * 100, 1),
                }
                for r in rules
            ]
            st.dataframe(rows, hide_index=True, use_container_width=True)

st.info(
    "Los archivos `data/dq_report.json` y `data/lineage.jsonl` recogen todos estos resultados para las etapas siguientes."
)
