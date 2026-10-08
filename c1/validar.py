"""Comprobaciones duras del banco (la parte automática del QUALITY_AGENT)."""

import re
from collections import Counter

from c1.revision import ESTADOS_PREGUNTA
from c1.store import Store

REQUISITOS_APROBADA = ("concepto_id", "epigrafe_id", "explicacion", "fuente_id", "fecha_validacion", "dificultad")
UMBRAL_SESGO = 0.35


def validar(store: Store) -> dict:
    errores, avisos = [], []
    temas = {t["id"] for b in store.read("programa.json", {"bloques": []})["bloques"] for t in b["temas"]}
    fuentes = {f["id"] for f in store.read("fuentes.json", [])}
    preguntas = store.preguntas()

    ids = Counter((q["id"], q["version"]) for q in preguntas)
    errores += [f"{i}@v{v}: id duplicado" for (i, v), n in ids.items() if n > 1]

    for q in preguntas:
        ref = f"{q['id']}@v{q['version']}"
        opts = q.get("opciones") or {}
        if sorted(opts) != list("abcd"):
            errores.append(f"{ref}: debe tener exactamente las opciones a, b, c y d")
        elif len({o.strip().lower() for o in opts.values()}) != 4 or not all(o.strip() for o in opts.values()):
            errores.append(f"{ref}: opciones vacías o repetidas")
        if q.get("correcta") not in opts:
            errores.append(f"{ref}: respuesta correcta inexistente")
        if q.get("tema_id") not in temas:
            errores.append(f"{ref}: tema {q.get('tema_id')} no está en el programa")
        if q.get("fuente_id") not in fuentes:
            errores.append(f"{ref}: fuente {q.get('fuente_id')} no registrada")
        if q.get("estado") not in ESTADOS_PREGUNTA:
            errores.append(f"{ref}: estado desconocido {q.get('estado')}")
        if q.get("estado") == "aprobada":
            faltan = [c for c in REQUISITOS_APROBADA if not q.get(c)]
            if faltan:
                errores.append(f"{ref}: aprobada sin {', '.join(faltan)}")

    activas = [q for q in preguntas if q.get("estado") != "retirada"]
    claves = Counter(re.sub(r"\s+", " ", q["enunciado"].strip().lower()) for q in activas)
    avisos += [f"Enunciado repetido {n} veces: «{k[:80]}»" for k, n in claves.items() if n > 1]

    reparto = Counter(q["correcta"] for q in activas)
    total = sum(reparto.values()) or 1
    for letra, n in sorted(reparto.items()):
        if n / total > UMBRAL_SESGO:
            avisos.append(f"Sesgo de posición: la {letra} es correcta en el {100 * n / total:.0f} % del banco")

    return {"errores": errores, "avisos": avisos, "preguntas": len(preguntas),
            "reparto_correctas": dict(sorted(reparto.items()))}
