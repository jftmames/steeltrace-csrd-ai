from __future__ import annotations

import streamlit as st

from app_utils import PATHS, ROOT_DIR, load_text

st.title("SHACL & Linaje RDF")
st.caption("Validación semántica sobre el grafo ESRS")

st.markdown(
    """
    El agente **SHACL.validate** toma los JSON normalizados y los materializa como nodos RDF.
    Luego aplica tres shapes ESRS (E1, S1, G1) y persiste tanto el log de conformidad como el
    linaje (`ontology/linaje.ttl`).
    """
)

validation_log = load_text(PATHS["validation_log"], "Aún no existe ontology/validation.log")
lineage_ttl = load_text(ROOT_DIR / "ontology" / "linaje.ttl", "Aún no existe ontology/linaje.ttl")

col1, col2 = st.columns(2)
with col1:
    st.write("### Resultado SHACL")
    st.code(validation_log[:4000], language="shell")
with col2:
    st.write("### Trazabilidad RDF (fragmento)")
    st.code(lineage_ttl[:4000], language="turtle")

st.markdown("---")

st.write("### Secuencia de pasos")
st.markdown(
    """
    1. **Construcción del grafo** con sujetos `E1Record`, `S1Record` y `G1Record`.
    2. **Evidencia vinculada**: cada nodo apunta al archivo JSON de origen.
    3. **Validación SHACL**: se ejecutan `contracts/shacl_e1.ttl`, `shacl_s1.ttl` y `shacl_g1.ttl`.
    4. **Persistencia**: `ontology/validation.log` captura conformidad y `ontology/linaje.ttl` conserva el grafo.
    """
)

st.info(
    "Estos artefactos son consumidos por RAGA (para citar evidencias) y por el gate EEE (para verificar rastreabilidad)."
)
