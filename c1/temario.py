"""Ingesta del temario de la academia (PDF) con trazabilidad por página.

El PDF es la fuente principal. De cada tema se guarda:
- la fuente (hash, páginas, fecha del PDF) en `fuentes.json`;
- el texto por página en `temario/texto/<tema>.jsonl` (para citar tema y página exactos);
- el índice de epígrafes y las normas de referencia en `temario/<tema>.json`.

El índice se extrae automáticamente del «ÍNDICE DE CONTENIDOS» del PDF y queda
como `extraido_automaticamente` hasta que el alumno lo valide.
"""

import datetime as _dt
import hashlib
import re
import subprocess
import unicodedata
from pathlib import Path

from c1.store import Store, hoy

RE_EPIGRAFE = re.compile(r"^\s*(\d{1,2}(?:\.\d{1,2}){0,3})\.?\s+(\S.*?)\s*$")
RE_INDICE = re.compile(r"ÍNDICE\s+DE\s+CONTENIDOS")
ANTIGUEDAD_RIESGO_DIAS = 2 * 365


def _norm(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t).strip()


def paginas_pdf(pdf: Path) -> list:
    """Texto por página (pdftotext separa páginas con salto de página)."""
    salida = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], check=True, capture_output=True).stdout
    paginas = salida.decode("utf-8", "replace").split("\f")
    return paginas[:-1] if paginas and not paginas[-1].strip() else paginas


def fecha_pdf(pdf: Path):
    try:
        info = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True).stdout.decode("utf-8", "replace")
    except (OSError, subprocess.CalledProcessError):
        return None
    m = re.search(r"CreationDate:\s+\w{3} (\w{3})\s+(\d+) [\d:]+ (\d{4})", info)
    if not m:
        return None
    return _dt.datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%b %d %Y").date().isoformat()


def normas_referencia(paginas: list) -> list:
    for p in paginas[:5]:
        if "NORMAS LEGISLATIVAS" in p:
            normas, actual = [], None
            for linea in p.splitlines()[1:]:
                s = linea.strip()
                if not s or s.isdigit():
                    continue
                if s.startswith("-"):
                    actual = s.lstrip("- ").strip()
                    if actual:
                        normas.append(actual)
                elif normas:
                    normas[-1] += " " + s
            return [re.sub(r"\s+", " ", n) for n in normas]
    return []


def indice(paginas: list):
    """Devuelve (epigrafes, pagina_inicio_cuerpo). Las páginas se cuentan desde 1."""
    inicio = next((i for i, p in enumerate(paginas[:8]) if RE_INDICE.search(p)), None)
    if inicio is None:
        return [], 1
    epigrafes, vistos, cuerpo = [], set(), None
    i = inicio
    while i < len(paginas) and cuerpo is None:
        continua = False  # un título partido solo continúa en la línea siguiente de la misma página
        for linea in paginas[i].splitlines():
            m = RE_EPIGRAFE.match(linea)
            s = linea.strip()
            if not s:
                continue
            if m and len(s) < 140:
                num = m.group(1)
                if num in vistos:  # la numeración se repite: empieza el cuerpo del tema
                    cuerpo = i
                    break
                vistos.add(num)
                epigrafes.append({"numero": num, "titulo": re.sub(r"\s+", " ", m.group(2))})
                continua = not m.group(2).rstrip().endswith(".")
            elif continua and not s.isdigit() and s.upper() == s:
                epigrafes[-1]["titulo"] += " " + re.sub(r"\s+", " ", s)
                continua = not s.endswith(".")
            else:
                continua = False
        i += 1
    cuerpo = cuerpo if cuerpo is not None else inicio + 1
    return epigrafes, cuerpo + 1


def localizar_epigrafes(epigrafes: list, paginas: list, pagina_cuerpo: int):
    """Asigna a cada epígrafe la primera página del cuerpo donde aparece su encabezado."""
    desde = pagina_cuerpo - 1
    for e in epigrafes:
        clave = _norm(e["titulo"])[:25]
        for i in range(desde, len(paginas)):
            for linea in paginas[i].splitlines():
                m = RE_EPIGRAFE.match(linea)
                s = linea.strip()
                numerado = m and m.group(1) == e["numero"] and _norm(m.group(2))[:12] == clave[:12]
                # Los epígrafes principales aparecen en el cuerpo sin número, centrados y en mayúsculas.
                sin_numero = (s and s.upper() == s and len(s) < 100 and len(clave) >= 6
                              and _norm(s)[:15] == clave[:15])
                if numerado or sin_numero:
                    e["pagina_ini"] = i + 1
                    desde = i
                    break
            if "pagina_ini" in e:
                break
        e.setdefault("pagina_ini", None)
    # Un epígrafe sin encabezado localizable empieza donde su primer subepígrafe.
    for e, sig in zip(epigrafes, epigrafes[1:]):
        if not e["pagina_ini"] and sig["numero"].startswith(e["numero"] + ".") and sig["pagina_ini"]:
            e["pagina_ini"] = sig["pagina_ini"]
            e["pagina_aproximada"] = True
    conocidas = [e for e in epigrafes if e["pagina_ini"]]
    for a, b in zip(conocidas, conocidas[1:]):
        a["pagina_fin"] = b["pagina_ini"]
    if conocidas:
        conocidas[-1]["pagina_fin"] = len(paginas)
    for e in epigrafes:
        e.setdefault("pagina_fin", None)
    return epigrafes


def importar(pdf: Path, tema_id: str, store: Store, ruta_publica=None):
    temas = {t["id"]: t for b in store.read("programa.json")["bloques"] for t in b["temas"]}
    if tema_id not in temas:
        raise SystemExit(f"{tema_id} no está en el programa")
    paginas = paginas_pdf(pdf)
    sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
    fecha = fecha_pdf(pdf)

    fuentes = store.read("fuentes.json", [])
    previa = next((f for f in fuentes if f.get("tema_id") == tema_id and f["tipo"] == "temario_pdf"), None)
    if previa and previa["sha256"] == sha:
        return {"tema": tema_id, "sin_cambios": True}
    fid = f"SRC-TEMARIO-{tema_id}" + (f"-v{sum(1 for f in fuentes if f.get('tema_id') == tema_id) + 1}" if previa else "")
    antiguedad = (_dt.date.fromisoformat(hoy()) - _dt.date.fromisoformat(fecha)).days if fecha else None
    fuente = {"id": fid, "tipo": "temario_pdf", "tema_id": tema_id, "titulo": pdf.name,
              "ruta": ruta_publica or str(pdf), "sha256": sha, "paginas": len(paginas), "fecha_pdf": fecha,
              "fecha_registro": hoy(),
              "nota": "Temario de la academia: fuente principal del sistema."
                      + (" PDF de hace más de dos años: comprobar vigencia normativa antes de fijar datos."
                         if antiguedad and antiguedad > ANTIGUEDAD_RIESGO_DIAS else "")}
    if previa:
        previa["sustituida_por"] = fid  # la versión anterior se conserva
    fuentes.append(fuente)
    store.write("fuentes.json", fuentes, accion="registrar_fuente", entidad=fid,
                motivo=f"PDF del temario para {tema_id}" + (f" (sustituye a {previa['id']})" if previa else ""))

    texto = "".join(__import__("json").dumps({"pagina": n, "texto": p}, ensure_ascii=False) + "\n"
                    for n, p in enumerate(paginas, 1))
    store.write_text(f"temario/texto/{tema_id}.jsonl", texto, accion="importar_texto_temario", entidad=tema_id,
                     motivo=f"Texto por página de {pdf.name} ({len(paginas)} páginas)")

    epigrafes, cuerpo = indice(paginas)
    epigrafes = localizar_epigrafes(epigrafes, paginas, cuerpo)
    for e in epigrafes:
        e["id"] = f"{tema_id}-E{e['numero']}"
    datos = {"tema_id": tema_id, "fuente_id": fid, "paginas": len(paginas), "fecha_pdf": fecha,
             "normas_referencia": normas_referencia(paginas), "pagina_inicio_cuerpo": cuerpo,
             "estado_indice": "extraido_automaticamente", "epigrafes": epigrafes}
    store.write(f"temario/{tema_id}.json", datos, accion="importar_indice_temario", entidad=tema_id,
                motivo=f"{len(epigrafes)} epígrafes extraídos del índice del PDF (pendiente de validar)")
    return {"tema": tema_id, "paginas": len(paginas), "epigrafes": len(epigrafes),
            "sin_pagina": [e["numero"] for e in epigrafes if not e["pagina_ini"]], "fecha_pdf": fecha}


def epigrafe_de_pagina(store: Store, tema_id: str, pagina: int):
    datos = store.read(f"temario/{tema_id}.json")
    mejor = None
    for e in (datos or {}).get("epigrafes", []):
        if e["pagina_ini"] and e["pagina_ini"] <= pagina:
            if mejor is None or e["pagina_ini"] >= mejor["pagina_ini"]:
                mejor = e
    return mejor


def buscar(store: Store, consulta: str, tema_id=None, limite=10):
    """Localiza un texto en el temario: tema, epígrafe probable, página y fragmento literal."""
    patron = _norm(consulta)
    resultados = []
    for p in store.glob("temario/texto/*.jsonl"):
        if tema_id and p.stem != tema_id:
            continue
        for ev in store.events(p.relative_to(store.root).as_posix()):
            lineas = ev["texto"].splitlines()
            for i, linea in enumerate(lineas):
                if patron in _norm(linea):
                    frag = " ".join(l.strip() for l in lineas[max(0, i - 1): i + 3] if l.strip())
                    e = epigrafe_de_pagina(store, p.stem, ev["pagina"])
                    resultados.append({"tema_id": p.stem, "pagina": ev["pagina"],
                                       "epigrafe": f"{e['numero']} {e['titulo']}" if e else None,
                                       "fragmento": re.sub(r"\s+", " ", frag)[:400]})
                    break
            if len(resultados) >= limite:
                return resultados
    return resultados
