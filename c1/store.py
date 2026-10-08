"""Acceso a los datos canónicos (JSON y JSONL en el directorio de datos).

Reglas:
- El contenido (programa, preguntas, flashcards...) se guarda en JSON legible.
- Lo que ocurre (auditoría, respuestas, alertas) se guarda en JSONL y solo se añade.
- Toda escritura de contenido deja un evento en la auditoría.
"""

import datetime as _dt
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROMANOS = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6}


def ahora() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def hoy() -> str:
    return _dt.date.today().isoformat()


def tema_id(bloque_romano: str, tema: str) -> str:
    """('III', 'T03') -> 'B3-T03'."""
    return f"B{ROMANOS[bloque_romano]}-{tema}"


class Store:
    def __init__(self, root=None):
        self.root = Path(root or os.environ.get("C1_DATA") or REPO / "data")

    # --- contenido JSON ---
    def path(self, rel: str) -> Path:
        return self.root / rel

    def exists(self, rel: str) -> bool:
        return self.path(rel).exists()

    def read(self, rel: str, default=None):
        p = self.path(rel)
        if not p.exists():
            return default
        return json.loads(p.read_text(encoding="utf-8"))

    def write(self, rel: str, data, *, accion: str, entidad: str, motivo: str, actor="c1"):
        p = self.path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        existia = p.exists()
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.audit(accion=accion, entidad=entidad, motivo=motivo, actor=actor,
                   detalle={"archivo": rel, "sobrescrito": existia})

    def write_text(self, rel: str, text: str, *, accion: str, entidad: str, motivo: str, actor="c1"):
        p = self.path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        existia = p.exists()
        p.write_text(text, encoding="utf-8")
        self.audit(accion=accion, entidad=entidad, motivo=motivo, actor=actor,
                   detalle={"archivo": rel, "sobrescrito": existia})

    def glob(self, pattern: str):
        return sorted(self.root.glob(pattern))

    # --- eventos JSONL (solo añadir) ---
    def append(self, rel: str, evento: dict):
        p = self.path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")

    def events(self, rel: str):
        p = self.path(rel)
        if not p.exists():
            return []
        return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

    def audit(self, *, accion, entidad, motivo, actor="c1", detalle=None):
        n = len(self.events("eventos/auditoria.jsonl")) + 1
        self.append("eventos/auditoria.jsonl", {
            "id": f"AUD-{n:06d}", "fecha": ahora(), "actor": actor, "accion": accion,
            "entidad": entidad, "motivo": motivo, "detalle": detalle or {},
        })

    # --- colecciones ---
    def preguntas(self):
        out = []
        for p in self.glob("preguntas/*.json"):
            out.extend(json.loads(p.read_text(encoding="utf-8")))
        return out

    def flashcards(self):
        out = []
        for p in self.glob("flashcards/*.json"):
            out.extend(json.loads(p.read_text(encoding="utf-8")))
        return out

    def alertas(self):
        """Estado actual de cada alerta, reconstruido desde sus eventos."""
        estado = {}
        for ev in self.events("eventos/alertas.jsonl"):
            if ev["tipo"] == "creada":
                estado[ev["alerta"]["id"]] = dict(ev["alerta"], estado="abierta")
            elif ev["tipo"] in ("revisada", "descartada"):
                estado[ev["id"]]["estado"] = ev["tipo"]
        return list(estado.values())

    def crear_alerta(self, alerta: dict, motivo: str):
        n = len(self.alertas()) + 1
        alerta = dict(alerta, id=f"ALR-{n:04d}", creada=ahora())
        self.append("eventos/alertas.jsonl", {"tipo": "creada", "fecha": ahora(), "alerta": alerta})
        self.audit(accion="crear_alerta", entidad=alerta["id"], motivo=motivo)
        return alerta
