from __future__ import annotations

import streamlit as st

from app_utils import PATHS, load_text

st.title("Reporte XBRL")
st.caption("Serialización digital del paquete regulatorio")

xbrl_xml = load_text(PATHS["xbrl"], "Aún no existe xbrl/informe.xbrl")
xbrl_log = load_text(PATHS["xbrl_log"], "Aún no existe xbrl/validation.log")

st.markdown(
    """
    Aquí se muestra el XML generado a partir de los KPIs aprobados.
    El esquema `xbrl/schema/basic_xbrl.xsd` se usa para validar la estructura.
    """
)

col1, col2 = st.columns(2)
with col1:
    st.write("### XML generado")
    st.code(xbrl_xml[:4000], language="xml")
with col2:
    st.write("### Log de validación")
    st.code(xbrl_log[:4000], language="text")

st.info("El archivo XBRL y su log se añaden al manifiesto de evidencias y quedan listos para descarga/auditoría.")
