import sys

# Metadata for Pipeline Steps
# Defines the command, description, and governance role for each step.

STEPS_METADATA = [
    {
        "name": "MCP.ingest",
        "label": "1. Recolección y Limpieza",
        "command": [sys.executable, "scripts/mcp_ingest.py"],
        "description": "Tomamos los datos 'sucios' de las facturas de energía, RRHH y ética, y los organizamos. Es como lavar las verduras antes de cocinar: nos aseguramos de que no falte nada y que los números tengan sentido.",
        "role": "Data Steward (Automated)",
        "output_artifact": "data/dq_report.json"
    },
    {
        "name": "SHACL.validate",
        "label": "2. Verificación de Reglas (SHACL)",
        "command": [sys.executable, "scripts/shacl_validate.py"],
        "description": "Consultamos el libro de reglas oficiales (ESRS). Verificamos que los datos cumplan estrictamente con lo que pide la ley europea. Si algo no encaja, salta una alarma aquí.",
        "role": "Ontology Guardian (Automated)",
        "output_artifact": "ontology/validation.log"
    },
    {
        "name": "RAGA.compute",
        "label": "3. Análisis Inteligente (RAGA)",
        "command": [sys.executable, "scripts/raga_compute.py"],
        "description": "Una Inteligencia Artificial revisa los datos aprobados para calcular los indicadores clave (KPIs). Además, escribe una explicación sencilla de por qué dio ese resultado, citando la ley.",
        "role": "AI Analyst (RAGA)",
        "output_artifact": "raga/explain.json"
    },
    {
        "name": "EEE.gate",
        "label": "4. Control de Calidad AI (Gate)",
        "command": [sys.executable, "scripts/eee_gate.py"],
        "description": "Un 'profesor' automático revisa el trabajo de la IA. Si la explicación es inventada o no tiene pruebas (alucinación), se bloquea el reporte. Solo pasa lo que es 100% confiable.",
        "role": "Compliance Officer (Automated Gate)",
        "output_artifact": "ops/gate_report.json"
    },
    {
        "name": "XBRL.generate",
        "label": "5. Creación del Reporte Oficial",
        "command": [sys.executable, "scripts/xbrl_generate.py"],
        "description": "Convertimos todos los resultados a un formato digital especial (XBRL) que es el que exigen los reguladores. Es como poner la carta en el sobre oficial del gobierno.",
        "role": "Reporting Agent",
        "output_artifact": "xbrl/informe.xbrl"
    },
    {
        "name": "EVIDENCE.build",
        "label": "6. Sellado de Seguridad",
        "command": [sys.executable, "scripts/evidence_build.py"],
        "description": "Metemos todo (datos, reglas, cálculos) en una 'caja fuerte digital' y le ponemos un sello criptográfico. Así garantizamos que nadie cambió nada después de la auditoría.",
        "role": "Notary (Crypto)",
        "output_artifact": "evidence/evidence_manifest.json"
    }
]

# Legacy simplified list for pipeline_run.py compatibility
STEPS = [(s["name"], s["command"]) for s in STEPS_METADATA]
