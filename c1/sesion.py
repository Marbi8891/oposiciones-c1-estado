"""Tests en modo evaluado: selección, corrección determinista y registro de errores.

Flujo: `c1 test` crea una sesión con preguntas (sin mostrar soluciones) →
el alumno responde con letra y confianza → `c1 corregir` registra cada respuesta,
la clasifica (real / dudas / azar / error / en blanco) y abre un error por cada fallo.
El tipo de error y la explicación los añade después Claude con `c1 clasificar-error`.
"""

import random
import re
from collections import Counter, defaultdict

from c1.store import Store, ahora, hoy

TIPOS_ERROR = {
    "K": "desconocimiento", "M": "olvido", "C": "confusión entre conceptos", "R": "lectura incorrecta",
    "N": "número, plazo o mayoría", "A": "artículo", "E": "excepción", "O": "órgano o competencia",
    "S": "estrategia / exceso de confianza", "G": "adivinación", "D": "normativa desactualizada", "T": "terminología",
}
RE_RESPUESTA = re.compile(r"^(\d+)\s*[:.)=-]?\s*([abcd-])\s*([?*]?)$", re.I)
SESIONES = "eventos/sesiones.jsonl"
RESPUESTAS = "eventos/respuestas.jsonl"
ERRORES = "eventos/errores.jsonl"


def _siguiente(store: Store, rel: str, prefijo: str, ancho=6) -> int:
    ids = [e.get("id", "") for e in store.events(rel)]
    nums = [int(i.split("-")[-1]) for i in ids if i.startswith(prefijo)]
    return max(nums, default=0) + 1


def crear(store: Store, *, temas=None, n=20, modo="tema", semilla=None) -> dict:
    """Selecciona preguntas practicables (no marcadas ni retiradas). modo: tema | errores."""
    preguntas = [q for q in store.preguntas() if q["estado"] in ("aprobada", "en_revision")]
    if temas:
        preguntas = [q for q in preguntas if q["tema_id"] in temas]
    if modo == "errores":
        falladas = {r["pregunta_id"] for r in store.events(RESPUESTAS) if r["clase"] == "ERROR"}
        preguntas = [q for q in preguntas if q["id"] in falladas]
    if not preguntas:
        raise SystemExit("No hay preguntas que cumplan el filtro.")
    vistas = Counter(r["pregunta_id"] for r in store.events(RESPUESTAS))
    rng = random.Random(semilla)
    rng.shuffle(preguntas)
    preguntas.sort(key=lambda q: (q["estado"] != "aprobada", vistas[q["id"]]))  # primero aprobadas y menos vistas
    elegidas = preguntas[:n]
    sid = f"SES-{hoy().replace('-', '')}-{_siguiente(store, SESIONES, 'SES-' + hoy().replace('-', '')):02d}"
    sesion = {"id": sid, "tipo": "creada", "fecha": ahora(), "modo": modo, "temas": temas or [],
              "preguntas": [{"id": q["id"], "version": q["version"]} for q in elegidas]}
    store.append(SESIONES, sesion)
    store.audit(accion="crear_test", entidad=sid, motivo=f"{len(elegidas)} preguntas, modo {modo}, temas {temas or 'todos'}")
    return sesion


def enunciados(store: Store, sesion: dict) -> list:
    por_id = {q["id"]: q for q in store.preguntas()}
    out = []
    for i, ref in enumerate(sesion["preguntas"], 1):
        q = por_id[ref["id"]]
        out.append({"n": i, "id": q["id"], "tema_id": q["tema_id"], "enunciado": q["enunciado"],
                    "opciones": q["opciones"], "en_revision": q["estado"] != "aprobada"})
    return out


def sesion(store: Store, sid: str) -> dict:
    eventos = [e for e in store.events(SESIONES) if e["id"] == sid]
    if not eventos:
        raise SystemExit(f"Sesión {sid} inexistente")
    s = dict(eventos[0])
    s["corregida"] = any(e["tipo"] == "corregida" for e in eventos)
    return s


def parsear(texto: str) -> dict:
    """'1a 2b? 3c* 4-' → {1: ('a','seguro'), 2: ('b','dudoso'), 3: ('c','azar'), 4: (None,'blanco')}."""
    out = {}
    for token in re.split(r"[\s,;]+", texto.strip()):
        if not token:
            continue
        m = RE_RESPUESTA.match(token)
        if not m:
            raise SystemExit(f"Respuesta no entendida: «{token}». Formato: 1a, 2b? (duda), 3c* (azar), 4- (en blanco)")
        letra = m.group(2).lower()
        conf = {"": "seguro", "?": "dudoso", "*": "azar"}[m.group(3)]
        out[int(m.group(1))] = (None, "blanco") if letra == "-" else (letra, conf)
    return out


def clase(acierto: bool, confianza: str) -> str:
    if confianza == "blanco":
        return "EN BLANCO"
    if not acierto:
        return "ERROR"
    return {"seguro": "ACIERTO REAL", "dudoso": "ACIERTO POR DUDAS", "azar": "ACIERTO POR AZAR"}[confianza]


def corregir(store: Store, sid: str, texto: str, minutos=None) -> dict:
    s = sesion(store, sid)
    if s["corregida"]:
        raise SystemExit(f"{sid} ya está corregida: las respuestas no se sobrescriben.")
    respuestas = parsear(texto)
    faltan = [i for i in range(1, len(s["preguntas"]) + 1) if i not in respuestas]
    if faltan:
        raise SystemExit(f"Faltan respuestas para: {faltan} (usa «n-» para dejarla en blanco)")
    por_id = {q["id"]: q for q in store.preguntas()}
    n_rsp = _siguiente(store, RESPUESTAS, "RSP-")
    n_err = _siguiente(store, ERRORES, "ERR-")
    detalle = []
    for i, ref in enumerate(s["preguntas"], 1):
        q = por_id[ref["id"]]
        marcada, conf = respuestas[i]
        acierto = marcada == q["correcta"]
        c = clase(acierto, conf)
        rid = f"RSP-{n_rsp:06d}"
        n_rsp += 1
        store.append(RESPUESTAS, {"id": rid, "pregunta_id": q["id"], "pregunta_version": q["version"],
                                  "tema_id": q["tema_id"], "sesion_id": sid, "marcada": marcada, "acierto": acierto,
                                  "confianza": conf, "clase": c, "fecha": ahora(),
                                  "pregunta_en_revision": q["estado"] != "aprobada"})
        fila = {"n": i, "pregunta_id": q["id"], "tema_id": q["tema_id"], "marcada": marcada, "correcta": q["correcta"],
                "texto_correcta": q["opciones"][q["correcta"]], "clase": c, "respuesta_id": rid}
        if c == "ERROR":
            eid = f"ERR-{n_err:06d}"
            n_err += 1
            store.append(ERRORES, {"id": eid, "tipo_evento": "abierto", "fecha": ahora(), "respuesta_id": rid,
                                   "pregunta_id": q["id"], "tema_id": q["tema_id"], "sesion_id": sid,
                                   "marcada": marcada, "correcta": q["correcta"]})
            fila["error_id"] = eid
        detalle.append(fila)
    clases = Counter(f["clase"] for f in detalle)
    store.append(SESIONES, {"id": sid, "tipo": "corregida", "fecha": ahora(), "minutos": minutos,
                            "resultado": dict(clases)})
    store.audit(accion="corregir_test", entidad=sid, motivo=f"{len(detalle)} respuestas: {dict(clases)}")
    total = len(detalle)
    return {"sesion": sid, "total": total, "clases": dict(clases),
            "acierto_bruto_pct": round(100 * sum(1 for f in detalle if f["clase"].startswith("ACIERTO")) / total),
            "acierto_real_pct": round(100 * clases["ACIERTO REAL"] / total), "detalle": detalle}


def clasificar_error(store: Store, eid: str, tipo: str, explicacion: str, concepto=None) -> dict:
    tipo = tipo.upper()
    if tipo not in TIPOS_ERROR:
        raise SystemExit(f"Tipo {tipo} desconocido. Válidos: {', '.join(f'{k}={v}' for k, v in TIPOS_ERROR.items())}")
    if not any(e["id"] == eid and e["tipo_evento"] == "abierto" for e in store.events(ERRORES)):
        raise SystemExit(f"{eid} no existe")
    ev = {"id": eid, "tipo_evento": "clasificado", "fecha": ahora(), "tipo": tipo, "explicacion": explicacion,
          "concepto": concepto}
    store.append(ERRORES, ev)
    store.audit(accion="clasificar_error", entidad=eid, motivo=f"{tipo} ({TIPOS_ERROR[tipo]}) · {concepto or '-'}")
    return ev


def errores(store: Store) -> list:
    """Estado actual de cada error (apertura + última clasificación)."""
    out = {}
    for e in store.events(ERRORES):
        if e["tipo_evento"] == "abierto":
            out[e["id"]] = dict(e, tipo=None, explicacion=None, concepto=None)
        elif e["tipo_evento"] == "clasificado":
            out[e["id"]].update(tipo=e["tipo"], explicacion=e["explicacion"], concepto=e["concepto"])
    return list(out.values())


def informe_errores(store: Store, dias=14, hoy_iso=None) -> dict:
    import datetime as _dt
    hoy_d = _dt.date.fromisoformat(hoy_iso or hoy())
    resp = store.events(RESPUESTAS)
    por_tema = defaultdict(Counter)
    for r in resp:
        por_tema[r["tema_id"]][r["clase"]] += 1
    temas = []
    for t, c in por_tema.items():
        n = sum(c.values())
        temas.append({"tema_id": t, "respuestas": n, "acierto_real_pct": round(100 * c["ACIERTO REAL"] / n),
                      "error_pct": round(100 * c["ERROR"] / n), "clases": dict(c)})
    temas.sort(key=lambda x: x["acierto_real_pct"])
    errs = errores(store)
    recientes = [e for e in errs if (hoy_d - _dt.date.fromisoformat(e["fecha"][:10])).days <= dias]
    clave = lambda e: (e["concepto"] or e["pregunta_id"]).strip().lower()  # noqa: E731
    reincidentes = Counter(clave(e) for e in recientes)
    return {
        "temas_peor_a_mejor": temas,
        "errores_total": len(errs), "sin_clasificar": [e["id"] for e in errs if not e["tipo"]],
        "por_tipo": dict(Counter(e["tipo"] or "sin clasificar" for e in errs)),
        "recurrentes_ultimos_dias": {k: v for k, v in reincidentes.most_common() if v >= 2},
        "top10": Counter(clave(e) for e in errs).most_common(10), "dias": dias,
    }
