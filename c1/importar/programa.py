"""Importa el programa (45 temas) y el estado declarado del sistema anterior.

Fuentes: `00_SEGUIMIENTO.md` (títulos de los 45 temas) y `PROGRESO.md`
(estado a 30/08/2026). El estado anterior se guarda tal cual como
"declarado"; no se convierte en evidencia de dominio.
"""

import hashlib
import re
from pathlib import Path

from c1.store import ROMANOS, Store, hoy

RE_BLOQUE = re.compile(r"^## Bloque ([IVX]+) — (.+?)(?: \(\d+ temas.*)?$")
RE_FILA = re.compile(r"^\| (T\d\d) \| (.+?) \|(.*)$")
RE_FECHA = re.compile(r"(\d\d)/(\d\d)/(\d{4})")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _iso(texto: str):
    m = RE_FECHA.search(texto or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def parsear_tablas(md: str):
    """Devuelve {bloque_romano: (nombre_bloque, [(tema, titulo, [resto de celdas])])}."""
    bloques, actual = {}, None
    for linea in md.splitlines():
        m = RE_BLOQUE.match(linea.strip())
        if m:
            actual = m.group(1)
            bloques[actual] = (m.group(2).strip(), [])
            continue
        m = RE_FILA.match(linea.strip())
        if m and actual:
            celdas = [c.strip() for c in m.group(3).split("|")]
            bloques[actual][1].append((m.group(1), m.group(2).strip(), [c for c in celdas if c != ""]))
    return bloques


def importar(seguimiento: Path, progreso: Path, store: Store):
    seg = parsear_tablas(seguimiento.read_text(encoding="utf-8"))
    prog = parsear_tablas(progreso.read_text(encoding="utf-8"))

    fuentes = store.read("fuentes.json", [])
    f_seg = {"id": "SRC-LEGACY-0001", "tipo": "seguimiento_propio", "titulo": "00_SEGUIMIENTO.md (sistema anterior, 29/08/2026)",
             "ruta": "legacy/sistema_anterior/00_SEGUIMIENTO.md", "sha256": _sha256(seguimiento), "fecha_registro": hoy(),
             "nota": "Títulos del programa copiados por el alumno; pendiente cotejar con el anexo de la convocatoria en BOE."}
    f_prog = {"id": "SRC-LEGACY-0002", "tipo": "seguimiento_propio", "titulo": "PROGRESO.md (sistema anterior, 30/08/2026)",
              "ruta": "legacy/sistema_anterior/PROGRESO.md", "sha256": _sha256(progreso), "fecha_registro": hoy(),
              "nota": "Estado declarado; el dominio 2/5 era provisional, sin test resuelto."}
    ids = {f["id"] for f in fuentes}
    fuentes += [f for f in (f_seg, f_prog) if f["id"] not in ids]
    store.write("fuentes.json", fuentes, accion="registrar_fuentes", entidad="fuentes",
                motivo="Fuentes del sistema anterior usadas en la migración")

    programa = {"fuente_id": f_seg["id"], "verificado_contra_convocatoria": False, "bloques": []}
    estado = {"fuente_id": f_prog["id"], "fecha_estado": "2026-08-30", "temas": {}}
    for romano, (nombre, filas) in seg.items():
        prog_filas = {t: (titulo, resto) for t, titulo, resto in prog.get(romano, (None, []))[1]}
        temas = []
        for t, titulo, _ in filas:
            tid = f"B{ROMANOS[romano]}-{t}"
            # PROGRESO tiene títulos completos donde 00_SEGUIMIENTO los abrevió con "...".
            titulo_final = prog_filas[t][0] if t in prog_filas and "..." in titulo else titulo
            temas.append({"id": tid, "numero": int(t[1:]), "titulo_oficial": titulo_final})
            if t in prog_filas:
                resto = prog_filas[t][1]
                estado["temas"][tid] = {
                    "estado_declarado": resto[0],
                    "dominio_declarado": int(resto[1]) if resto[1].isdigit() else None,
                    "primera_pasada": _iso(resto[2]),
                    "repasos_referencia": [d for d in (_iso(x) for x in resto[3:6]) if d],
                    "test_resuelto": resto[6] if len(resto) > 6 else None,
                }
        programa["bloques"].append({"id": f"B{ROMANOS[romano]}", "romano": romano, "nombre": nombre, "temas": temas})

    store.write("programa.json", programa, accion="importar_programa", entidad="programa",
                motivo="Mapa de 45 temas desde 00_SEGUIMIENTO.md")
    store.write("estado_declarado.json", estado, accion="importar_estado_declarado", entidad="estado_declarado",
                motivo="Estado del sistema anterior (PROGRESO.md, 30/08/2026), conservado como declaración, no como evidencia")
    return programa, estado
