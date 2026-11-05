"""Fase 1, reproducible: temario de la academia + estado declarado a 03/09/2026.

python3 scripts/migracion_f1.py [carpeta_pdf]   (por defecto /mnt/project-files)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from c1 import temario  # noqa: E402
from c1.importar import programa  # noqa: E402
from c1.store import REPO, Store  # noqa: E402

PDFS = {
    "B1-T01": "T01 (Bloque I) - C1 Estado - 23062023-3.pdf",
    "B1-T02": "T02 (Bloque I) - C1 Estado.pdf",
    "B1-T03": "T03 (Bloque I) - C1 Estado.pdf",
    "B1-T04": "T04 (Bloque I) - C1 Estado - 01062020.pdf",
    "B1-T05": "T05 (Bloque I) - C1 Estado.pdf",
    "B1-T06": "T06 (Bloque I) - C1 Estado - 25102024.pdf",
    "B1-T07": "T07 (Bloque I) - C1 Estado - 13082024.pdf",
    "B1-T08": "T08 (Bloque I) - C1 Estado 220124.pdf",
    "B1-T09": "T09 (Bloque I) - C1 Estado.pdf",
    "B1-T10": "T10 (Bloque I) - C1 Estado - 09072020.pdf",
    "B1-T11": "T11 (Bloque I) - C1 Estado - 21102024.pdf",
    "B2-T03": "T03 (Bloque II) - C1 Estado.pdf",
}


def main():
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/project-files")
    store = Store()

    print("Nuevos con primera pasada:",
          programa.importar_estado(REPO / "legacy/sistema_anterior/PROGRESO.md", store, "2026-09-03"))

    config = store.read("config.json")
    config["alumno"] = {
        "turno": "reserva discapacidad",
        "nota": "Declarado en PERFIL_ALUMNO.md (15/09/2026). Condiciones de reserva y adaptaciones: "
                "pendiente de confirmar en las bases de la convocatoria de la OEP 2026.",
    }
    config["examen"]["formato_referencia"] = {
        "estado": "PENDIENTE DE VERIFICACIÓN",
        "descripcion": "Convocatoria OEP 2025 según CAMBIOS_LEGISLATIVOS.md (15/09/2026): 70 preguntas (40 temario + 30 "
                       "ofimática) + supuesto práctico a elegir entre 2 (20 preguntas), máximo 100 minutos.",
        "fuente": "BOE-A-2025-26262 (no contrastado todavía por este sistema)",
    }
    config["restriccion_15_09"] = (
        "El CLAUDE.md del sistema anterior (15/09/2026) pedía no convertir la preparación en un proyecto de "
        "programación salvo petición explícita. El alumno pidió este sistema expresamente el 05/10/2026 y aprobó el "
        "diseño el 07/10/2026. Se mantiene el espíritu: no ampliar herramientas fuera de las fases aprobadas.")
    store.write("config.json", config, accion="actualizar_config", entidad="config",
                motivo="Turno de acceso, formato de referencia pendiente y restricción de alcance del 15/09")

    for tema, nombre in PDFS.items():
        pdf = carpeta / nombre
        print(temario.importar(pdf, tema, store, ruta_publica=f"/mnt/project-files/{nombre}"))


if __name__ == "__main__":
    main()
