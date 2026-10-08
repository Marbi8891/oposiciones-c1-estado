"""Importa el banco de chuleta-c1 (index.html) como material EN REVISIÓN.

Nada de lo importado queda "aprobado": las preguntas no traen explicación,
fuente, epígrafe ni fecha de validación. Además:
- Se rebarajan las opciones para corregir el sesgo de posición del banco
  original (70 % de respuestas "b"). El orden original queda registrado.
- Se detectan enunciados duplicados con claves distintas.
"""

import hashlib
import json
import random
import re
from pathlib import Path

from c1.store import Store, hoy, tema_id

LETRAS = "abcd"
# Opciones que se refieren a otras por su letra: no se pueden rebarajar.
RE_REFERENCIA_POSICIONAL = re.compile(r"\b(opci[oó]n(es)?|respuestas?)\s+[abcd]\b|\b[abcd]\)\s*y\s*[abcd]\)", re.I)


def extraer_constantes(html: str) -> dict:
    """Extrae los literales JSON de `const NOMBRE = [...]` del script embebido."""
    dec = json.JSONDecoder()
    out = {}
    for m in re.finditer(r"const (FLASHCARDS|QUIZBANK|STUDYBANK)\s*=\s*", html):
        out[m.group(1)], _ = dec.raw_decode(html, m.end())
    return out


def posiciones_equilibradas(n: int, semilla: str):
    """Lista de n letras lo más repartida posible, en orden pseudoaleatorio reproducible."""
    letras = [LETRAS[i % 4] for i in range(n)]
    random.Random(semilla).shuffle(letras)
    return letras


def rebarajar(opts, correcta, destino):
    """Coloca la opción correcta en `destino` y mantiene el orden relativo del resto."""
    idx = LETRAS.index(correcta)
    resto = [o for i, o in enumerate(opts) if i != idx]
    nuevas = []
    for letra in LETRAS:
        nuevas.append(opts[idx] if letra == destino else resto.pop(0))
    return nuevas


def importar(html_path: Path, store: Store, origen_repo="Marbi8891/chuleta-c1", commit=None):
    html = html_path.read_text(encoding="utf-8")
    datos = extraer_constantes(html)
    sha = hashlib.sha256(html.encode("utf-8")).hexdigest()

    fuentes = store.read("fuentes.json", [])
    fuente = {"id": "SRC-CHULETA-0001", "tipo": "resumen_propio",
              "titulo": f"chuleta-c1 index.html ({origen_repo}{'@' + commit if commit else ''})",
              "ruta": f"https://github.com/{origen_repo}", "sha256": sha, "fecha_registro": hoy(),
              "nota": "Resúmenes y tests generados en el sistema anterior a partir del temario de la academia. "
                      "Material secundario: no sustituye al PDF del temario."}
    fuentes = [f for f in fuentes if f["id"] != fuente["id"]] + [fuente]
    store.write("fuentes.json", fuentes, accion="registrar_fuente", entidad=fuente["id"],
                motivo="Banco chuleta-c1 importado en la Fase 0")

    # Resúmenes
    for s in datos["STUDYBANK"]:
        tid = tema_id(s["bloque"], s["tema"])
        cab = (f"<!-- fuente: {fuente['id']} · resumen_propio · importado {hoy()} · "
               f"no es el temario original -->\n\n")
        store.write_text(f"resumenes/{tid}.md", cab + s["markdown"].rstrip() + "\n",
                         accion="importar_resumen", entidad=tid, motivo="Resumen de chuleta-c1")

    # Preguntas
    n = 0
    vistos = {}
    por_tema = {}
    for bloque in datos["QUIZBANK"]:
        tid = tema_id(bloque["bloque"], bloque["tema"])
        destinos = posiciones_equilibradas(len(bloque["questions"]), semilla=f"rebarajar:{tid}")
        lista = []
        for q, destino in zip(bloque["questions"], destinos):
            n += 1
            qid = f"Q-{n:06d}"
            opts, correcta = q["opts"], q["answer"]
            motivos = ["Importada sin explicación, fuente, epígrafe, concepto ni fecha de validación."]
            if any(RE_REFERENCIA_POSICIONAL.search(o) for o in opts):
                nuevas, nueva_correcta = list(opts), correcta
                motivos.append("No rebarajada: una opción se refiere a otra por su letra.")
            else:
                nuevas, nueva_correcta = rebarajar(opts, correcta, destino), destino
            clave = re.sub(r"\s+", " ", q["stem"].strip().lower())
            if clave in vistos:
                motivos.append(f"Enunciado duplicado de {vistos[clave]}.")
            vistos.setdefault(clave, qid)
            lista.append({
                "id": qid, "version": 1, "tema_id": tid, "epigrafe_id": None, "concepto_id": None,
                "dificultad": None, "tipo": None,
                "enunciado": q["stem"], "opciones": dict(zip(LETRAS, nuevas)), "correcta": nueva_correcta,
                "explicacion": None, "fuente_id": fuente["id"], "norma_articulo": None, "fecha_validacion": None,
                "estado": "en_revision",
                "origen": {"tipo": "importada_chuleta", "archivo": bloque["file"], "num": q["num"],
                           "opciones_originales": opts, "correcta_original": correcta},
                "revision": motivos,
            })
        por_tema[tid] = lista
    for tid, lista in por_tema.items():
        store.write(f"preguntas/{tid}.json", lista, accion="importar_preguntas", entidad=tid,
                    motivo=f"{len(lista)} preguntas de chuleta-c1, opciones rebarajadas, estado en_revision")

    # Flashcards
    fcs = {}
    for i, f in enumerate(datos["FLASHCARDS"], 1):
        tid = tema_id(f["bloque"], f["tema"])
        fcs.setdefault(tid, []).append({
            "id": f"FC-{i:05d}", "version": 1, "tema_id": tid, "concepto_id": None, "tipo": "hueco",
            "anverso": f["front"], "reverso": f["back"], "mnemotecnia": None, "dato_literal": None,
            "fuente_id": fuente["id"], "estado": "en_revision",
            "origen": {"tipo": "importada_chuleta", "id_original": f["id"]},
        })
    for tid, lista in fcs.items():
        store.write(f"flashcards/{tid}.json", lista, accion="importar_flashcards", entidad=tid,
                    motivo=f"{len(lista)} flashcards de chuleta-c1, estado en_revision")

    return {"resumenes": len(datos["STUDYBANK"]), "preguntas": n, "flashcards": len(datos["FLASHCARDS"])}
