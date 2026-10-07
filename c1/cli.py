"""CLI `python -m c1 <orden>`. Toda escritura pasa por aquí y deja auditoría."""

import argparse
import json
import sys
from pathlib import Path

from c1 import build as _build, progreso as _progreso, validar as _validar
from c1.store import REPO, Store


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="c1", description="Motor del sistema de preparación C1")
    ap.add_argument("--datos", help="directorio de datos (por defecto data/ del repo o $C1_DATA)")
    sub = ap.add_subparsers(dest="orden", required=True)

    p = sub.add_parser("progreso", aliases=["estado"], help="informe de progreso con datos reales")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("validar", help="comprobaciones duras del banco")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("build", help="regenera el índice SQLite")
    p.add_argument("--destino", default=str(REPO / "build" / "c1.db"))
    sub.add_parser("alertas", help="alertas abiertas")
    p = sub.add_parser("auditoria", help="últimos eventos de auditoría")
    p.add_argument("-n", type=int, default=20)
    p = sub.add_parser("importar-programa")
    p.add_argument("seguimiento", type=Path)
    p.add_argument("progreso", type=Path)
    p = sub.add_parser("importar-chuleta")
    p.add_argument("html", type=Path)
    p.add_argument("--commit")

    a = ap.parse_args(argv)
    store = Store(a.datos)

    if a.orden in ("progreso", "estado"):
        datos = _progreso.calcular(store)
        print(json.dumps(datos, ensure_ascii=False, indent=2) if a.json else _progreso.texto(datos))
    elif a.orden == "validar":
        r = _validar.validar(store)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=2))
        else:
            print(f"{r['preguntas']} preguntas · reparto de correctas {r['reparto_correctas']}")
            for e in r["errores"]:
                print("ERROR", e)
            for w in r["avisos"]:
                print("AVISO", w)
        return 1 if r["errores"] else 0
    elif a.orden == "build":
        db = _build.build(store, a.destino)
        n = db.execute("SELECT COUNT(*) FROM pregunta").fetchone()[0]
        print(f"Índice creado en {a.destino} ({n} preguntas)")
    elif a.orden == "alertas":
        for al in store.alertas():
            print(f"{al['id']} [{al['estado']}] {al['titulo']}")
            print(f"   acción recomendada: {al.get('accion_recomendada')}")
    elif a.orden == "auditoria":
        for ev in store.events("eventos/auditoria.jsonl")[-a.n:]:
            print(f"{ev['id']} {ev['fecha']} {ev['actor']} {ev['accion']} {ev['entidad']} · {ev['motivo']}")
    elif a.orden == "importar-programa":
        from c1.importar import programa
        prog, _ = programa.importar(a.seguimiento, a.progreso, store)
        print(f"{sum(len(b['temas']) for b in prog['bloques'])} temas importados")
    elif a.orden == "importar-chuleta":
        from c1.importar import chuleta
        print(chuleta.importar(a.html, store, commit=a.commit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
