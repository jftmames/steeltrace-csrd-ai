# STEELTRACE™ | CSRD+AI Compliance MVP

> **Automated Sustainability Reporting with Auditable AI Governance**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## 📋 Overview

**STEELTRACE™** is a Proof of Concept (PoC) designed to demonstrate how **Generative AI** can be safely integrated into **CSRD (Corporate Sustainability Reporting Directive)** workflows.

This MVP showcases a fully automated pipeline that ingests raw enterprise data, validates it against semantic rules (SHACL), generates explainable metrics (RAGA), and produces a legally compliant XBRL report, all while maintaining a cryptographic audit trail.

### Key Features

*   **🛡️ Multi-Agent Architecture**: Modular pipeline with specialized agents for Ingestion, Validation, Calculation, and Reporting.
*   **🧠 RAGA (Retrieval-Augmented Generation with Audit)**: AI explanations for every KPI, grounded in ESRS regulations.
*   **⚖️ EEE-Gate (Epistemic-Explicit-Evidence)**: A novel governance gate that blocks AI hallucinations from entering the final report.
*   **🔗 Merkle Audit Trail**: Every data point and decision is hashed and linked, creating an immutable chain of custody.
*   **📊 XBRL Generation**: Automatic generation of digital reports compliant with ESEF/taxonomy standards.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/) (optional, or standard pip)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-org/steeltrace-mvp.git
    cd steeltrace-mvp
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

La interfaz se divide ahora en **mini-aplicaciones Streamlit** (pestañas en la barra lateral) para ver paso a paso cada
componente del pipeline: ingesta+DQ, validación SHACL, RAGA, gate EEE, XBRL y evidencias.

> ¿Quieres saber qué expone cada pestaña? Consulta la guía detallada en `docs/multipage_walkthrough.md`.

---

## 🏗️ Architecture

The solution follows a strict linear pipeline orchestrated by `scripts/pipeline_run.py`:

1.  **MCP.ingest**: Normalizes raw JSON inputs (Energy, HR, Ethics) and checks Data Quality (completeness, validity).
2.  **SHACL.validate**: Maps data to an RDF Knowledge Graph and validates against ESRS ontologies (E1, S1, G1).
3.  **RAGA.compute**: Calculates sustainability KPIs (e.g., CO2e, Gender Pay Gap) and generates AI-driven explanations.
4.  **EEE.gate**: Evaluates the confidence of the AI's output. Only high-confidence outputs pass to the final report.
5.  **XBRL.generate**: serializes the validated data into the official XBRL format.
6.  **EVIDENCE.build**: Bundles all logs and artifacts into a Merkle Tree for external auditing.

---

## 📂 Project Structure

```
├── app.py                 # Streamlit UI Entry Point
├── contracts/             # Data Contracts (Schemas, SHACL shapes, DQ rules)
├── data/                  # Input samples and Normalized data
├── ontology/              # ESRS Ontology (OWL) and RDF Knowledge Graph
├── ops/                   # Operational logs (SLO, Gate Reports)
├── rag/                   # Vector Index for RAGA (ESRS regulations)
├── raga/                  # Generated KPIs and Explanations
├── scripts/               # Python processing modules
│   ├── pipeline_run.py    # Orchestrator
│   ├── mcp_ingest.py      # Data Ingestion
│   ├── ...
└── xbrl/                  # Generated XBRL reports and Schemas
```

## 🤝 Contribution

This is an academic/consulting MVP. Contributions to improve the ontology or add new ESRS modules are welcome.

## 📄 License

This project is licensed under the **CC BY 4.0** license.
