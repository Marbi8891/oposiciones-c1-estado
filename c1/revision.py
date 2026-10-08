"""Verificaciones normativas y marcas de revisión.

Una verificación registra qué dice la fuente oficial, dónde y cuándo se
consultó. Marcar una pregunta para revisión cambia solo su estado: el
contenido no se toca hasta que el alumno apruebe una versión nueva.
"""

from c1.store import Store, ahora

ESTADOS_PREGUNTA = ("borrador", "en_revision", "aprobada", "marcada_revision", "retirada")


def registrar_verificacion(store: Store, *, norma, articulo, texto_literal, url, fecha_consulta,
                           version_consolidada=None, modificaciones=(), estado="VERIFICADO VIGENTE", nota=None):
    verifs = store.read("normas/verificaciones.json", [])
    vid = f"VER-{len(verifs) + 1:04d}"
    verifs.append({
        "id": vid, "norma": norma, "articulo": articulo, "texto_literal": texto_literal,
        "fuente": {"tipo": "boe", "url": url, "fecha_consulta": fecha_consulta,
                   "version_consolidada": version_consolidada},
        "modificaciones": list(modificaciones), "estado": estado, "nota": nota,
    })
    store.write("normas/verificaciones.json", verifs, accion="registrar_verificacion", entidad=vid,
                motivo=f"{norma} {articulo}: {estado}")
    return vid


def buscar_pregunta(store: Store, *, archivo, num):
    for q in store.preguntas():
        o = q.get("origen") or {}
        if o.get("archivo") == archivo and o.get("num") == num:
            return q
    return None


def _modificar(store: Store, qid: str, cambio, accion: str, motivo: str, actor: str):
    for path in store.glob("preguntas/*.json"):
        rel = path.relative_to(store.root).as_posix()
        lista = store.read(rel)
        for q in lista:
            if q["id"] == qid:
                cambio(q)
                q["revision"] = list(q.get("revision") or []) + [f"[{ahora()}] {motivo}"]
                store.write(rel, lista, accion=accion, entidad=qid, actor=actor, motivo=motivo)
                return q
    raise KeyError(qid)


def marcar_revision(store: Store, qid: str, motivo: str, actor="c1"):
    """Pasa la pregunta a marcada_revision sin tocar su contenido."""
    return _modificar(store, qid, lambda q: q.update(estado="marcada_revision"), "marcar_revision", motivo, actor)


def anotar(store: Store, qid: str, nota: str, actor="c1"):
    """Añade una nota de revisión sin cambiar estado ni contenido."""
    return _modificar(store, qid, lambda q: None, "anotar_revision", nota, actor)
