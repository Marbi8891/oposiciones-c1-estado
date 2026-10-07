"""Construye el índice SQLite a partir de los datos canónicos."""

import json
import sqlite3
from pathlib import Path

from c1.store import Store

SCHEMA = Path(__file__).with_name("schema.sql")


def build(store: Store, destino=":memory:") -> sqlite3.Connection:
    if destino != ":memory:":
        Path(destino).parent.mkdir(parents=True, exist_ok=True)
        Path(destino).unlink(missing_ok=True)
    db = sqlite3.connect(destino)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SCHEMA.read_text(encoding="utf-8"))

    for f in store.read("fuentes.json", []):
        db.execute("INSERT INTO fuente VALUES (?,?,?,?,?,?,?)",
                   (f["id"], f["tipo"], f["titulo"], f.get("ruta"), f.get("sha256"), f.get("fecha_registro"), f.get("nota")))
    for b in store.read("programa.json", {"bloques": []})["bloques"]:
        db.execute("INSERT INTO bloque VALUES (?,?,?)", (b["id"], b["romano"], b["nombre"]))
        for t in b["temas"]:
            db.execute("INSERT INTO tema VALUES (?,?,?,?)", (t["id"], b["id"], t["numero"], t["titulo_oficial"]))
    for tid, e in store.read("estado_declarado.json", {"temas": {}})["temas"].items():
        db.execute("INSERT INTO estado_declarado VALUES (?,?,?,?,?)",
                   (tid, e["estado_declarado"], e["dominio_declarado"], e["primera_pasada"], e["test_resuelto"]))
    for q in store.preguntas():
        db.execute("INSERT INTO pregunta VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (q["id"], q["version"], q["tema_id"], q["epigrafe_id"], q["concepto_id"], q["dificultad"],
                    q["enunciado"], q["correcta"], q["fuente_id"], q["norma_articulo"], q["fecha_validacion"],
                    q["estado"], json.dumps(q.get("origen"), ensure_ascii=False)))
    for f in store.flashcards():
        db.execute("INSERT INTO flashcard VALUES (?,?,?,?,?,?,?)",
                   (f["id"], f["version"], f["tema_id"], f["concepto_id"], f["tipo"], f["fuente_id"], f["estado"]))
    for r in store.events("eventos/respuestas.jsonl"):
        db.execute("INSERT INTO respuesta VALUES (?,?,?,?,?,?,?,?,?)",
                   (r["id"], r["pregunta_id"], r["pregunta_version"], r.get("sesion_id"), r["marcada"],
                    int(r["acierto"]), r["confianza"], r.get("tiempo_ms"), r["fecha"]))
    for a in store.alertas():
        db.execute("INSERT INTO alerta VALUES (?,?,?,?,?)", (a["id"], a["tipo"], a["titulo"], a["estado"], a["creada"]))
        for qid in a.get("preguntas", []):
            db.execute("INSERT INTO alerta_pregunta VALUES (?,?)", (a["id"], qid))
    for v in store.read("normas/verificaciones.json", []):
        db.execute("INSERT INTO verificacion VALUES (?,?,?,?,?,?)",
                   (v["id"], v["norma"], v["articulo"], v["estado"], v["fuente"]["url"], v["fuente"]["fecha_consulta"]))
    for p in store.glob("resumenes/*.md"):
        db.execute("INSERT INTO resumen VALUES (?,?)", (p.stem, p.relative_to(store.root).as_posix()))
    for a in store.events("eventos/auditoria.jsonl"):
        db.execute("INSERT INTO auditoria VALUES (?,?,?,?,?,?)",
                   (a["id"], a["fecha"], a["actor"], a["accion"], a["entidad"], a["motivo"]))
    db.commit()
    return db
