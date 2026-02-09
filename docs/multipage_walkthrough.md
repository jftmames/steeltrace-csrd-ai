# Guía de las mini‑aplicaciones Streamlit

Esta guía explica **qué hace cada pestaña** del UI y cómo evidencia la complejidad paso a paso del pipeline CSRD+AI. Cada página se alimenta de los artefactos producidos por `scripts/pipeline_run.py` (o de respaldos en `evidence/defaults/`) para que siempre haya ejemplos completos visibles.

## 1. MCP Ingest & Data Quality (`pages/01_MCP_Ingest_and_DQ.py`)
- **Objetivo**: Normalizar datos crudos (energía, RRHH, ética) y aplicar reglas de calidad.
- **Entradas**: JSON de `data/raw/` y contratos de datos en `contracts/`.
- **Proceso**: Ejecuta `scripts/mcp_ingest.py` y valida perfiles DQ.
- **Salidas mostradas**: Dominios DQ, fallos por regla y el dataset normalizado en `data/normalized/`.

## 2. SHACL y RDF (`pages/02_SHACL_and_RDF.py`)
- **Objetivo**: Proyectar los JSON normalizados a un grafo RDF y verificar conformidad con ESRS.
- **Entradas**: Datos de `data/normalized/` y shapes en `contracts/shacl/`.
- **Proceso**: Llama a `scripts/shacl_validate.py` con la ontología de `ontology/`.
- **Salidas mostradas**: Informe SHACL, tripletas RDF y los grafos resultantes en `ontology/output/`.

## 3. RAGA KPIs (`pages/03_RAGA.py`)
- **Objetivo**: Calcular KPIs (CO₂e, brecha salarial, sanciones) y explicar cada métrica con grounding regulatorio.
- **Entradas**: Grafos RDF + índice vectorial en `rag/index/`.
- **Proceso**: `scripts/raga_run.py` ejecuta retrieval y generación con citas ESRS.
- **Salidas mostradas**: Tabla de KPIs con evidencia, chunks citados y trazas de cálculo intermedio.

## 4. EEE Gate (`pages/04_EEE_Gate.py`)
- **Objetivo**: Bloquear salidas de IA sin evidencia suficiente mediante el filtro Epistemic‑Explicit‑Evidence.
- **Entradas**: KPIs explicados desde RAGA.
- **Proceso**: `scripts/eee_gate.py` puntúa precisión, explicitez y soporte documental.
- **Salidas mostradas**: Score EEE, decisión global y motivos por los que se aprueba/rechaza cada ítem.

## 5. XBRL (`pages/05_XBRL.py`)
- **Objetivo**: Serializar el reporte en formato XBRL y registrar el log de validación.
- **Entradas**: Datos validados + taxonomía en `xbrl/taxonomy/`.
- **Proceso**: `scripts/xbrl_generate.py` arma el documento y ejecuta validadores.
- **Salidas mostradas**: Archivo XBRL generado y errores/avisos de validación.

## 6. Evidencias & Merkle (`pages/06_Evidence_and_Merkle.py`)
- **Objetivo**: Consolidar logs, hashes y artefactos firmados para auditoría.
- **Entradas**: Reportes de cada fase y archivos en `evidence/`.
- **Proceso**: `evidence_build.py` construye el árbol de Merkle y empaqueta trazas.
- **Salidas mostradas**: Hash raíz, nodos intermedios y enlaces a artefactos de respaldo.

## Orquestador y ejemplos completos
- El botón **“Ejecutar pipeline completo”** en la barra lateral llama a `scripts/pipeline_run.py` para regenerar todos los artefactos.
- Si no se ejecuta manualmente, la UI carga **ejemplos de referencia** desde `evidence/defaults/` para que cada pestaña muestre insumos y resultados completos sin pasos vacíos.
