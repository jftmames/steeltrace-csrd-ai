from __future__ import annotations

import streamlit as st

from app_utils import DEFAULTS, PATHS, lineage_rows, load_json

st.title("Evidencias y cadena de custodia")
st.caption("Manifiesto Merkle + linaje de archivos")

manifest = load_json(PATHS["manifest"], DEFAULTS["manifest"])
lineage = lineage_rows(PATHS["lineage"])

st.markdown(
    """
    La fase **EVIDENCE.build** firma los artefactos generados y construye un árbol de Merkle.

    1. Calcula `sha256` de cada archivo clave (RAGA, SHACL, gate, XBRL).
    2. Concatena los hashes para obtener una **merkle_root**.
    3. Opcionalmente sella la raíz en una TSA (simulada en este MVP).
    4. Registra el linaje de archivos de entrada y salida en `data/lineage.jsonl`.
    """
)

col1, col2 = st.columns(2)
with col1:
    st.write("### Manifiesto de evidencias")
    st.json(manifest)
with col2:
    st.write("### Linaje de archivos (primeras líneas)")
    st.code("\n".join(lineage), language="json")

st.info("El manifiesto es el paquete final para auditores: incluye hashes, merkle_root y tokens TSA simulados.")
