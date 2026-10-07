"""Informe de progreso calculado solo a partir de datos registrados.

Regla de dominio (diseño §4.4): leer nunca sube de 1; el nivel 2 en adelante
exige respuestas evaluadas. En la Fase 0 el dominio se calcula por tema y se
limita a 3, porque los niveles 4 y 5 exigen repasos diferidos (Fases 1 y 2).
"""

from collections import Counter, defaultdict

from c1.store import Store, hoy

NIVEL_MAX_F0 = 3


def clasificar(respuesta: dict) -> str:
    """ACIERTO REAL / ACIERTO POR DUDAS / ACIERTO POR AZAR / ERROR."""
    if not respuesta["acierto"]:
        return "ERROR"
    return {"seguro": "ACIERTO REAL", "dudoso": "ACIERTO POR DUDAS", "azar": "ACIERTO POR AZAR"}[respuesta["confianza"]]


def dominio_tema(primera_pasada: bool, respuestas: list) -> int:
    if not respuestas:
        return 1 if primera_pasada else 0
    clases = [clasificar(r) for r in sorted(respuestas, key=lambda r: r["fecha"])]
    reales = clases.count("ACIERTO REAL")
    if reales == 0:
        return 1
    ultimas = clases[-5:]
    if len(ultimas) >= 5 and ultimas.count("ACIERTO REAL") / len(ultimas) >= 0.70:
        return min(3, NIVEL_MAX_F0)
    return 2


def calcular(store: Store) -> dict:
    programa = store.read("programa.json", {"bloques": []})
    declarado = store.read("estado_declarado.json", {"temas": {}})["temas"]
    preguntas = store.preguntas()
    q_tema = {q["id"]: q["tema_id"] for q in preguntas}
    respuestas = store.events("eventos/respuestas.jsonl")
    resp_tema = defaultdict(list)
    for r in respuestas:
        resp_tema[q_tema.get(r["pregunta_id"])].append(r)
    resumenes = {p.stem for p in store.glob("resumenes/*.md")}
    temario_pdf = {f.get("tema_id") for f in store.read("fuentes.json", []) if f["tipo"] == "temario_pdf"}
    estados_q = defaultdict(Counter)
    for q in preguntas:
        estados_q[q["tema_id"]][q["estado"]] += 1
    fc_tema = Counter(f["tema_id"] for f in store.flashcards())

    bloques = []
    for b in programa["bloques"]:
        temas = []
        for t in b["temas"]:
            d = declarado.get(t["id"])
            pasada = bool(d and d.get("primera_pasada"))
            rs = resp_tema.get(t["id"], [])
            temas.append({
                "id": t["id"], "titulo": t["titulo_oficial"],
                "primera_pasada_declarada": d.get("primera_pasada") if d else None,
                "estado_registrado": d is not None,
                "temario_pdf": t["id"] in temario_pdf, "resumen": t["id"] in resumenes,
                "preguntas": dict(estados_q.get(t["id"], {})), "flashcards": fc_tema.get(t["id"], 0),
                "respuestas": dict(Counter(clasificar(r) for r in rs)),
                "dominio": dominio_tema(pasada, rs),
            })
        bloques.append({"id": b["id"], "romano": b["romano"], "nombre": b["nombre"], "temas": temas})

    todos = [t for b in bloques for t in b["temas"]]
    return {
        "fecha": hoy(),
        "programa_verificado": programa.get("verificado_contra_convocatoria", False),
        "respuestas_evaluadas": len(respuestas),
        "clases_respuesta": dict(Counter(clasificar(r) for r in respuestas)),
        "bloques": bloques,
        "sin_estado_con_material": [t["id"] for t in todos
                                    if not t["estado_registrado"] and (t["resumen"] or t["preguntas"])],
        "temario_pdf_cargado": sum(t["temario_pdf"] for t in todos),
        "banco": dict(sum((Counter(t["preguntas"]) for t in todos), Counter())),
        "flashcards": sum(t["flashcards"] for t in todos),
        "tests_sin_resolver": sum(1 for t in todos if t["preguntas"] and not t["respuestas"]),
        "alertas_abiertas": [{"id": a["id"], "titulo": a["titulo"]} for a in store.alertas() if a["estado"] == "abierta"],
    }


def _pct(n, d):
    return f"{100 * n / d:.0f} %" if d else "—"


def texto(p: dict) -> str:
    total_temas = sum(len(b["temas"]) for b in p["bloques"])
    L = [f"PROGRESO C1 · datos a {p['fecha']}", ""]
    if p["respuestas_evaluadas"] == 0:
        L.append("Evidencia: SIN EVIDENCIA DE RENDIMIENTO. No hay ningún test resuelto en modo evaluado, "
                 "así que ningún tema puede pasar del nivel 1 (visto).")
    else:
        c = p["clases_respuesta"]
        n = p["respuestas_evaluadas"]
        L.append(f"Evidencia: {n} respuestas evaluadas · acierto real {_pct(c.get('ACIERTO REAL', 0), n)} · "
                 f"con dudas {_pct(c.get('ACIERTO POR DUDAS', 0), n)} · por azar {_pct(c.get('ACIERTO POR AZAR', 0), n)} · "
                 f"error {_pct(c.get('ERROR', 0), n)}")
    L.append(f"Programa: {total_temas} temas en {len(p['bloques'])} bloques"
             + ("" if p["programa_verificado"] else " (títulos pendientes de cotejar con la convocatoria en BOE)"))
    L.append("")
    for b in p["bloques"]:
        ts = b["temas"]
        pasada = sum(1 for t in ts if t["primera_pasada_declarada"])
        res = sum(t["resumen"] for t in ts)
        nq = sum(sum(t["preguntas"].values()) for t in ts)
        aprob = sum(t["preguntas"].get("aprobada", 0) for t in ts)
        media = sum(t["dominio"] for t in ts) / len(ts)
        L.append(f"Bloque {b['romano']} · {b['nombre']} ({len(ts)} temas)")
        L.append(f"  1ª pasada declarada {pasada}/{len(ts)} · resúmenes {res} · preguntas {nq} ({aprob} aprobadas) · "
                 f"dominio medio {media:.1f}/5")
    L.append("")
    if p["sin_estado_con_material"]:
        L.append("Temas con material pero sin estado registrado: " + ", ".join(p["sin_estado_con_material"])
                 + " (confirmar si se estudiaron)")
    L.append(f"Temario original (PDF de la academia) cargado: {p['temario_pdf_cargado']}/{total_temas} temas")
    banco = p["banco"]
    L.append(f"Banco: {sum(banco.values())} preguntas · " + ", ".join(f"{k} {v}" for k, v in sorted(banco.items()))
             + f" · flashcards {p['flashcards']}")
    L.append(f"Deuda: {p['tests_sin_resolver']} tests de tema generados y sin resolver en modo evaluado")
    if p["alertas_abiertas"]:
        L.append("Alertas abiertas:")
        L += [f"  {a['id']} · {a['titulo']}" for a in p["alertas_abiertas"]]
    return "\n".join(L)
