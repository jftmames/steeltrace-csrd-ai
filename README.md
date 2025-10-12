# STEELTRACE™ CSRD+AI — MVP académico (PoC)

Arquitectura reproducible para cumplimiento CSRD/ESRS y AI Act con:
- Ontología + SHACL (validación semántica)
- RAGA (razonamiento, KPIs, explicaciones)
- EEE-Gate (evidencia o no pasa)
- XBRL/FEUE (salida verificable)
- WORM + TSA (evidencias con valor legal)
- Observabilidad con SLOs p95

## Cómo ejecutar (resumen)
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

## Ejecutar en Binder

[![Launch Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jftmames/steeltrace-csrd-ai/HEAD?labpath=scripts%2Fsteeltrace_lab.ipynb&flush_cache=true) 


