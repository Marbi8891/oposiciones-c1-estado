"""Migración de la Fase 0, reproducible: python3 scripts/migracion_f0.py <chuleta index.html> [--commit SHA]

Deja constancia de cada paso en data/eventos/auditoria.jsonl.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from c1.importar import chuleta, programa  # noqa: E402
from c1.revision import anotar, buscar_pregunta, registrar_verificacion  # noqa: E402
from c1.store import REPO, Store  # noqa: E402

LEGACY = REPO / "legacy" / "sistema_anterior"

CONFIG = {
    "examen": {"fecha_estimada": "2027-05", "es_estimacion": True, "formato": None,
               "formato_nota": "Pendiente de verificar en la convocatoria (BOE-A-2025-26262, Anexo III)."},
    "disponibilidad": {"horas_semana_min": 10, "horas_semana_max": 15},
    "prioridades": ["DAW", "C1", "ciberseguridad"],
    "daw": {"horas_semana": None, "semanas_criticas": [], "nota": "Pendiente: el alumno aún no ha dado su carga DAW."},
    "politica_repasos": {
        "decision": "D2",
        "regla": "La academia marca los repasos de tema; el sistema solo sugiere a nivel de concepto.",
        "intervalos_dias": {"R1": 1, "R2": 3, "R3": 7, "R4": 14, "R5": 30, "R6": 60},
    },
    "test": {"preguntas_por_defecto": 20, "dificultad_objetivo": {"facil": 15, "media": 45, "dificil": 30, "muy_dificil": 10}},
    "origen": "legacy/sistema_anterior/CONFIG.yaml + diseño aprobado el 07/10/2026",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chuleta_html", type=Path)
    ap.add_argument("--commit")
    a = ap.parse_args()
    store = Store()
    if store.exists("programa.json"):
        sys.exit("data/ ya contiene datos: la migración solo se ejecuta una vez.")

    store.write("config.json", CONFIG, accion="crear_config", entidad="config",
                motivo="Parámetros del sistema anterior + decisiones D1/D2 aprobadas")
    programa.importar(LEGACY / "00_SEGUIMIENTO.md", LEGACY / "PROGRESO.md", store)
    print(chuleta.importar(a.chuleta_html, store, commit=a.commit))

    # La auditoría del 05/10/2026 señaló por error una contradicción en este plazo: ambas preguntas
    # (IV-T01 P7 e IV-T03 P2) dan como correcta «9 meses dentro de 18». Se verifica en BOE y se deja constancia.
    vid = registrar_verificacion(
        store, norma="Real Decreto Legislativo 5/2015 (TREBEP)", articulo="art. 10.1.d",
        texto_literal="El exceso o acumulación de tareas por plazo máximo de nueve meses, dentro de un periodo de dieciocho meses",
        url="https://www.boe.es/buscar/act.php?id=BOE-A-2015-11719", fecha_consulta="2026-10-07",
        version_consolidada="última actualización 03/10/2026",
        modificaciones=["Real Decreto-ley 14/2021, de 6 de julio (BOE-A-2021-11233)",
                        "Ley 20/2021, de 28 de diciembre (BOE-A-2021-21651)"],
        nota="Coincide con la clave de T01_Bloque_IV_test.md P7 y T03_Bloque_IV_test.md P2 (enunciado duplicado).")
    for archivo, num in (("T01_Bloque_IV_test.md", 7), ("T03_Bloque_IV_test.md", 2)):
        q = buscar_pregunta(store, archivo=archivo, num=num)
        assert "9 meses" in q["opciones"][q["correcta"]], q["id"]
        anotar(store, q["id"], f"Clave contrastada con BOE ({vid}): coincide con el texto vigente. Sigue en revisión "
                               "porque le faltan explicación, epígrafe y concepto.")

if __name__ == "__main__":
    main()
