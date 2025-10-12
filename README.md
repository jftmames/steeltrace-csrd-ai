# STEELTRACE™ CSRD+AI — MVP académico (PoC)

Arquitectura reproducible para cumplimiento CSRD/ESRS y AI Act con:
- Ontología + SHACL (validación semántica)
- RAGA (razonamiento, KPIs, explicaciones)
- EEE-Gate (evidencia o no pasa)
- XBRL/FEUE (salida verificable)
- WORM + TSA (evidencias con valor legal)
- Observabilidad con SLOs p95

## Cómo ejecutar (resumen)
El pipeline completo se ejecuta automáticamente desde la aplicación Streamlit para generar todos los artefactos de trazabilidad.
1. Carga datos de ejemplo en `data/samples/`
2. Valida schema + DQ → `contracts/`
3. SHACL → `ontology/`
4. KPIs → `raga/`
5. Gate → `ops/`
6. XBRL → `xbrl/`
7. Evidencias → `evidence/`

> Este repo es educativo/investigación. No es despliegue productivo.

## Licencias
- Código: MIT (LICENSE)
- Documentación: CC BY 4.0 (LICENSE-CC-BY-4.0.txt)

## Ejecutar el Reporte Interactivo (Streamlit) 🚀

Este PoC se lanza como una aplicación Streamlit. Para validar la aplicación:

1.  Abre el repositorio en **Codespaces** (o un entorno con Docker/Streamlit).
2.  Instala las dependencias: `pip install -r requirements.txt`
3.  Lanza la aplicación en el terminal: `streamlit run app.py`

**Nota:** La aplicación tiene un botón **"Ejecutar Pipeline y Recargar Reportes"** que orquesta todos los pasos del flujo (`mcp_ingest.py` hasta `evidence_build.py`) para generar y mostrar los artefactos de cumplimiento (DQ, EEE-Score, SLO, Kappa).

---

*(Puedes mantener el badge de Binder original si quieres ofrecer la opción de JupyterLab para inspeccionar el código, pero el enfoque principal es el reporte interactivo.)*

