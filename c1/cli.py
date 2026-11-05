"""CLI `python -m c1 <orden>`. Toda escritura pasa por aquí y deja auditoría."""

import argparse
import json
import sys
from pathlib import Path

from c1 import build as _build, progreso as _progreso, sesion as _sesion, temario as _temario, validar as _validar
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

    p = sub.add_parser("importar-estado", help="actualiza el estado declarado desde PROGRESO.md")
    p.add_argument("progreso", type=Path)
    p.add_argument("--fecha", required=True, help="fecha del PROGRESO.md (AAAA-MM-DD)")
    p = sub.add_parser("importar-temario", help="registra el PDF del temario de un tema")
    p.add_argument("pdf", type=Path)
    p.add_argument("--tema", required=True, help="p. ej. B1-T05")
    p = sub.add_parser("temario", help="índice de un tema con páginas y normas de referencia")
    p.add_argument("tema")
    p = sub.add_parser("buscar", help="localiza un texto en el temario (tema, epígrafe, página)")
    p.add_argument("consulta")
    p.add_argument("--tema")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("test", help="crea un test en modo evaluado")
    p.add_argument("--tema", action="append", help="repetible; sin él, todos los temas")
    p.add_argument("-n", type=int, default=20)
    p.add_argument("--modo", choices=["tema", "errores"], default="tema")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("corregir", help="corrige un test: «1a 2b? 3c* 4-»")
    p.add_argument("sesion")
    p.add_argument("respuestas")
    p.add_argument("--minutos", type=int)
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("clasificar-error")
    p.add_argument("error")
    p.add_argument("--tipo", required=True)
    p.add_argument("--explicacion", required=True)
    p.add_argument("--concepto")
    p = sub.add_parser("errores", help="registro de errores: temas, tipos y reincidencias")
    p.add_argument("--dias", type=int, default=14)
    p.add_argument("--json", action="store_true")

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
    elif a.orden == "importar-estado":
        from c1.importar import programa
        print("Temas nuevos con primera pasada:", programa.importar_estado(a.progreso, store, a.fecha))
    elif a.orden == "importar-temario":
        print(_temario.importar(a.pdf, a.tema, store))
    elif a.orden == "temario":
        d = store.read(f"temario/{a.tema}.json")
        if not d:
            print(f"{a.tema}: temario no cargado. Información no verificada para este tema.")
            return 1
        print(f"{a.tema} · {d['paginas']} páginas · PDF de {d['fecha_pdf']} · índice {d['estado_indice']}")
        print("Normas de referencia: " + "; ".join(d["normas_referencia"] or ["(el PDF no las indica)"]))
        for e in d["epigrafes"]:
            sangria = "  " * e["numero"].count(".")
            pag = f"p. {e['pagina_ini']}" + ("~" if e.get("pagina_aproximada") else "") if e["pagina_ini"] else "p. ?"
            print(f"  {sangria}{e['numero']} {e['titulo']} · {pag}")
    elif a.orden == "buscar":
        r = _temario.buscar(store, a.consulta, a.tema)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=2))
        elif not r:
            print("Sin resultados en el temario cargado: información no verificada.")
        for x in r if not a.json else []:
            print(f"[TEMARIO] {x['tema_id']} · p. {x['pagina']} · {x['epigrafe'] or 'epígrafe ?'}\n   «{x['fragmento']}»")
    elif a.orden == "test":
        s = _sesion.crear(store, temas=a.tema, n=a.n, modo=a.modo)
        preguntas = _sesion.enunciados(store, s)
        if a.json:
            print(json.dumps({"sesion": s["id"], "preguntas": preguntas}, ensure_ascii=False, indent=2))
        else:
            print(f"{s['id']} · {len(preguntas)} preguntas")
            for q in preguntas:
                marca = " (en revisión)" if q["en_revision"] else ""
                print(f"\n{q['n']}. {q['enunciado']}{marca}")
                for letra, texto in q["opciones"].items():
                    print(f"   {letra}) {texto}")
    elif a.orden == "corregir":
        r = _sesion.corregir(store, a.sesion, a.respuestas, a.minutos)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=2))
        else:
            print(f"{r['sesion']}: acierto bruto {r['acierto_bruto_pct']} % · acierto real {r['acierto_real_pct']} % · {r['clases']}")
            for f in r["detalle"]:
                print(f"  {f['n']}. {f['clase']}: marcó {f['marcada'] or '-'}, correcta {f['correcta']}) "
                      f"{f['texto_correcta']}" + (f" · {f['error_id']}" if f.get("error_id") else ""))
    elif a.orden == "clasificar-error":
        print(_sesion.clasificar_error(store, a.error, a.tipo, a.explicacion, a.concepto))
    elif a.orden == "errores":
        r = _sesion.informe_errores(store, a.dias)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=2))
        else:
            if not r["temas_peor_a_mejor"]:
                print("Sin respuestas evaluadas todavía.")
            for t in r["temas_peor_a_mejor"]:
                print(f"{t['tema_id']}: acierto real {t['acierto_real_pct']} % · error {t['error_pct']} % · {t['respuestas']} respuestas")
            print(f"Errores: {r['errores_total']} · por tipo {r['por_tipo']} · sin clasificar {len(r['sin_clasificar'])}")
            for k, v in r["recurrentes_ultimos_dias"].items():
                print(f"Has fallado «{k}» {v} veces en los últimos {r['dias']} días")
    return 0


if __name__ == "__main__":
    sys.exit(main())
