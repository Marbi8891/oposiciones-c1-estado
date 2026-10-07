# Sistema de preparación C1 — Auditoría y diseño (Fases 1 a 7)

Versión 1 · 05/10/2026 · Estado: **PROPUESTA, pendiente de aprobación. No se ha implementado nada.**

Convención de este documento: 🔎 = comprobado en archivos/fuentes (con referencia) · 💡 = propuesta de diseño · ⚠️ = pendiente de verificar o de decidir.

---

## 0. Auditoría

### 0.1 Qué hay realmente disponible

| Elemento | Dónde | Contenido real | Valor para el sistema |
|---|---|---|---|
| Carpeta compartida del proyecto | `/mnt/project-files/` | Vacía salvo tus 16 subidas de hoy | Persistencia entre hilos |
| Estado del sistema anterior | Tus subidas (CLAUDE.md, CONFIG.yaml, PERFIL_ALUMNO, PROGRESO, ERROR_LOG, REPASOS, SIMULACROS, SESIONES, CAMBIOS_LEGISLATIVOS, README, PROMPT_INICIO, 00_PLAN, 00_SEGUIMIENTO) | Sistema "Preparador Privado C1" basado en Markdown, fecha interna 30/08/2026 | Reglas pedagógicas ya pactadas + estado a migrar |
| OEP 2026 | `BOE-A-2026-9946.pdf` (subido 3 veces, md5 idéntico) | RD 387/2026: cuerpo 1135 = 2.077 libre + 223 PI = 2.300 plazas 🔎 (verificado en el PDF) | Contexto; no es temario |
| Repo `Marbi8891/chuleta-c1` (público) | `index.html` 647 KB | 25 resúmenes, 500 preguntas, 165 flashcards embebidos en JS; progreso en `localStorage` | Banco inicial a importar (con revisión) |
| Repo `Marbi8891/oposiciones-c1-estado` (privado) | GitHub | **Vacío, sin commits** 🔎 | Candidato natural para alojar el sistema |
| **Temario oficial de la academia (PDFs BLOQUE I–VI)** | Tu carpeta local `OPOSICIONES` | **No subido** | Debe ser la fuente principal: **falta** |
| `TEMARIO_MAP.md`, `ULTIMA_VUELTA.md`, `resumenes/`, `tests/` | Referenciados en README/CLAUDE.md | **No subidos** | Necesarios para migrar sin perder trabajo |

### 0.2 Hallazgos

1. ⚠️ **El temario no está.** Solo tengo resúmenes derivados (chuleta-c1) y los títulos de los 45 temas (en `00_SEGUIMIENTO.md`: I 11 · II 4 · III 7 · IV 9 · V 6 · VI 8). Los resúmenes son material secundario: el sistema no los tratará como fuente primaria. Hasta que subas los PDFs, todo contenido derivado de ellos irá marcado como `fuente: resumen_propio`.
2. **El estado está desincronizado entre versiones.** README dice 9 temas estudiados; PROGRESO (30/08) dice 22; chuleta-c1 (03/09) contiene 25 (incluye Bloque IV T01–T03). No hay registro de cuándo se trabajaron los tres temas del Bloque IV. Será el primer dato a confirmar contigo.
3. **No existe ningún dato real de rendimiento.** 0 tests resueltos en modo evaluado, ERROR_LOG vacío, 0 simulacros, dominio "2" puesto por defecto. El sistema arrancará honestamente en "sin evidencia" y no inventará métricas.
4. **El banco de 500 preguntas tiene un sesgo grave de posición** 🔎: la correcta es la **b en 352 (70,4 %)**, c en 78, a en 63 y d en 7. Contestando siempre "b" se saca un 70 %. Cualquier porcentaje obtenido con ese banco tal cual está inflado. Corrección propuesta: barajar opciones (transformación segura, registrada en auditoría).
5. ~~**El banco contradice a sus propios resúmenes**~~ **[Corrección 07/10/2026]** Error de lectura en la auditoría: las preguntas IV T01 P7 e IV T03 P2 dan ambas como correcta "9 meses dentro de 18", que coincide con el texto vigente del art. 10.1.d TREBEP (BOE, consultado el 07/10/2026). Es solo un enunciado duplicado. Los resúmenes sí indican que el PDF original de la academia del tema IV-3 recogía la redacción anterior a la reforma, lo que mantiene el riesgo de desactualización del punto 7.
6. **Las preguntas no tienen** explicación, fuente, artículo, epígrafe, dificultad ni fecha de validación. Hay 1 enunciado duplicado (el del punto 5) y 41 enunciados en forma negativa. Las 165 flashcards cubren solo los bloques I–III.
7. ⚠️ Uno de los PDFs de la academia se llama `T01 (Bloque I) - C1 Estado - 23062023-3.pdf` (según `00_SEGUIMIENTO.md`), lo que sugiere material de 2023. Riesgo de desactualización alto, sobre todo en los bloques III y IV.
8. **Conflicto de reglas a decidir:** tu CLAUDE.md (regla del 30/08/2026) dice que **el calendario de repasos lo marca la academia**, no Claude. El encargo de hoy pide un agente de repetición espaciada adaptativo. Propuesta en §2 (decisión D2).
9. **No hay datos de carga DAW** (horas, entregas, exámenes). Sin ellos el planificador no puede proteger DAW de verdad. Se pedirán en la Fase 2.
10. **Formato de examen no confirmado.** Existe la convocatoria de 18/12/2025 (BOE-A-2025-26262) con un Anexo III para este cuerpo, pero no he podido leer el anexo todavía ⚠️. Los simulacros usarán un formato configurable hasta verificarlo.
11. **Red:** desde este entorno la API de datos abiertos del BOE devuelve 403 en el proxy 🔎; la lectura web de boe.es sí funciona. Afecta al diseño del MCP de legislación (§3).

### 0.3 Lo que se conserva del sistema anterior

Las reglas que ya habías pactado son buenas y se mantienen como **política del sistema**: escala de dominio 0–5 con exigencia de evidencia diferida para el 5, códigos de error K/M/C/R/N/A/E/O/S/G, intervalos R1–R6 (1/3/7/14/30/60 días), umbrales de rendimiento, avanzar por orden dentro del bloque, preguntar antes de procesar lotes grandes, no inventar sesiones ni métricas. El cambio es **dónde viven los datos y quién calcula**: hoy todo es Markdown que Claude reescribe a mano (riesgo de deriva y de errores aritméticos); se pasa a datos estructurados calculados por código.

---

## FASE 1 — Arquitectura actual y propuesta

### 1.1 Arquitectura actual (diagnóstico)

```
Carpeta local OPOSICIONES (Cowork/Claude Code)
 ├─ PDFs academia (BLOQUE I–VI)        ← fuente, no accesible aquí
 ├─ CLAUDE.md + 10 archivos .md/.yaml   ← estado, editado a mano por Claude
 └─ resumenes/, tests/                  ← generados
chuleta-c1 (web estática)               ← copia de resúmenes/tests, progreso en localStorage
```

Problemas: el estado está en texto libre (no se puede consultar "errores de los últimos 14 días"), las métricas las "calcula" el modelo, no hay trazabilidad pregunta→fuente, no hay versionado salvo el que hagas tú y hay tres copias del progreso que no coinciden.

### 1.2 Arquitectura propuesta

Principio rector: **el modelo redacta, explica y clasifica; el código cuenta, programa y decide umbrales.** Así ninguna estadística, fecha de repaso o nivel de dominio puede ser alucinada.

```
                 ┌──────────────── Tú (hilos del proyecto / Claude Code) ────────────────┐
                 │  /hoy  /test  /repaso  /simulacro  /tema 7  "no entiendo esto" ...     │
                 └───────────────────────────────┬────────────────────────────────────────┘
                                                 ▼
                         ORCHESTRATOR (skill "tutor")  ── lee siempre `c1 estado`
                                                 │
      ┌──────────────┬──────────────┬────────────┼─────────────┬───────────────┬──────────────┐
      ▼              ▼              ▼            ▼             ▼               ▼              ▼
  TEMARIO        TEST/ADVERS.    CORRECTION    TEACHER      MEMORY        MOCK_EXAM     LEGISLATION
  (ingesta)      (genera)  ──▶   QUALITY       (explica)    (flashcards)  (informe)     + OFFICIAL_SOURCE
                                 (revisa, contexto aparte)                              + SYLLABUS_UPDATE
      │              │              │            │             │               │              │
      └──────────────┴──────────────┴─────┬──────┴─────────────┴───────────────┴──────────────┘
                                          ▼
              Motor determinista `c1` (Python, CLI): importación, banco, corrección,
              ERROR_LOG, ANALYTICS, SRS, dominio, PLANNER (con tope DAW), simulacros, alertas
                                          ▼
          Datos canónicos en Git (YAML/JSONL, append-only)  ──build──▶  SQLite (índice derivado)
          repo privado oposiciones-c1-estado                             para consultas rápidas
```

Decisiones técnicas:

| Decisión | Elección propuesta 💡 | Motivo |
|---|---|---|
| Lenguaje del motor | Python 3 + `sqlite3` estándar + `pytest` | Sin dependencias pesadas; disponible en todos los entornos (verificado: Python 3 y SQLite 3.45 aquí) |
| Datos canónicos | Archivos de texto en Git: YAML para contenido (temario, conceptos, preguntas, fuentes, normas) y **JSONL de eventos solo-añadir** para lo que pasa (respuestas, errores, repasos, sesiones, simulacros, cambios) | Versionado y auditoría gratis (`git log`), diffs legibles, nada se sobrescribe en silencio, sin conflictos de un `.db` binario compartido |
| Consultas | SQLite regenerado desde esos archivos (`c1 build`) | Consultas rápidas sin que la BD sea la fuente de verdad |
| Alojamiento | Repo privado `oposiciones-c1-estado` guardado en el proyecto, para que cada hilo lo tenga | Funciona igual en un hilo del proyecto, en Claude Code en la nube o en tu carpeta local (clonando el repo) |
| Agentes | Skills del repo (`.claude/skills/<agente>/SKILL.md`) + comandos `/hoy`, `/test`... | Nativos de Claude Code; versionados con el resto |
| Separación generador/revisor | QUALITY se ejecuta como subagente con contexto propio, sin ver el razonamiento del generador | Revisión independiente real |
| Procedencia del contenido | Cada afirmación servida se etiqueta `TEMARIO` / `VIGENTE` / `PEDAGÓGICO` | Requisito 1.6 |

⚠️ Decisión D1 (alojamiento): alternativa a lo anterior, todo en tu carpeta local mediante Remote Control. Recomiendo el repo porque sobrevive a cualquier sesión y queda auditado.

---

## FASE 2 — Agentes

Los 16 roles que pides se mantienen con su nombre (los podrás invocar e identificar), pero no todos deben ser un "agente LLM". Donde la tarea es cálculo, el rol es un módulo de código con una capa fina de explicación. Esto reduce coste, evita alucinaciones numéricas y es más fácil de probar.

| Rol | Implementación | Qué hace el modelo | Qué hace el código | Prioridad |
|---|---|---|---|---|
| ORCHESTRATOR / tutor | Skill | Decide qué agente interviene y redacta la recomendación | `c1 estado` y `c1 recomendar` devuelven deuda, repasos vencidos, temas débiles y presupuesto de tiempo | P1 |
| TEMARIO_AGENT | Skill + importador | Descompone el PDF en epígrafes y conceptos y clasifica A/B/C y 🔴🟠🟡⚪; genera fichas, esquemas y tablas citando página | Extrae texto (`pdftotext`), guarda hash del PDF y referencias de página, valida que toda cita apunte a texto existente | P1 |
| TEST_AGENT | Skill | Redacta preguntas desde conceptos con fuente | Asigna IDs, equilibra posición A/B/C/D, rechaza preguntas sin fuente | P1 |
| ADVERSARIAL_TEST_AGENT | Modo de TEST_AGENT (`--adversarial`) | Variantes de cambio de plazo/órgano/excepción a partir de la **matriz de confusiones** y tus errores reales | Selecciona conceptos con errores tipo C/N/O/E | P3 |
| QUALITY_AGENT | Subagente independiente | Revisa ambigüedad, doble respuesta, fuente inexistente, desactualización | Comprobaciones duras: 4 opciones distintas, 1 correcta, la cita existe en el temario o en la norma registrada, sin duplicados | P1 |
| CORRECTION_AGENT | Skill | Explica el porqué y propone el tipo de error | Registra la respuesta, calcula ACIERTO REAL/DUDAS/AZAR/ERROR y actualiza dominio y SRS | P1 |
| ERROR_LOG_AGENT | Módulo de código | Redacta el informe | Errores por tema/bloque/concepto, recurrentes ("4 fallos en 14 días"), evolución | P1 |
| SPACED_REPETITION_AGENT | Módulo de código | — | Programación por concepto (ver §4.4) | P2 |
| MEMORY_AGENT | Skill | Flashcards, preguntas inversas, mnemotecnias | Cada mnemotecnia queda enlazada al dato literal que codifica; QUALITY verifica que no lo altere | P2 |
| STUDY_PLANNER_AGENT | Código + skill | Redacta el plan | Calcula el presupuesto semanal con tope DAW (§5.6) y lo reparte | P2 |
| MOCK_EXAM_AGENT | Código + skill | Informe cualitativo | Compone el simulacro, cronometra, puntúa y compara con anteriores | P3 |
| ANALYTICS_AGENT | Módulo de código | Interpreta | Métricas (§4.5), incluida la distinción real/dudas/azar | P3 |
| TEACHER_AGENT | Skill | Explicación sencilla, jurídica, ejemplo, contraejemplo y pregunta de comprobación | Localiza el concepto y devuelve el texto fuente exacto que la explicación debe respetar | P1 (básico) |
| LEGISLATION_AGENT | Skill | Compara el texto del temario con el texto vigente | Registro de normas, versiones y diferencias | P4 |
| OFFICIAL_SOURCE_AGENT | Herramienta (MCP BOE) + lista blanca de dominios | — | Descarga solo de fuentes oficiales y guarda URL, fecha de consulta y hash | P4 |
| SYLLABUS_UPDATE_AGENT | Módulo de código | Redacta la alerta | Dado un artículo cambiado, encuentra por trazabilidad los epígrafes, preguntas y flashcards afectados y los marca `revisar` **sin modificarlos** | P4 |

Reglas comunes a todos los agentes (irán en el `CLAUDE.md` del repo):
- Ninguno escribe en los datos directamente: todo pasa por la CLI `c1`, que valida y deja rastro.
- Respuestas tipificadas: "Información no verificada", "Existe una discrepancia entre fuentes", "El temario puede estar desactualizado respecto a la normativa vigente".
- Ninguna pregunta o flashcard generada se presenta como oficial (ya lo exige tu CONFIG).

⚠️ **Decisión D2 (repasos):** propuesta: el motor SRS calcula a nivel de **concepto** y sugiere ("hay 12 conceptos en riesgo de olvido"), pero **el calendario de repasos de tema sigue marcándolo la academia**, como pactaste el 30/08. Si la academia dice "repasa el tema 3", el sistema prepara ese repaso priorizando los conceptos débiles del tema 3. El sistema nunca te dirá "hoy toca el tema X" solo por fecha, salvo que cambies esa regla.

---

## FASE 3 — MCP: evaluación

| MCP evaluado | ¿Hace falta? | Razón |
|---|---|---|
| Archivos/documentos | **No** | Lectura de archivos y `pdftotext` ya existen. Un MCP no añade capacidad. |
| Legislación/web oficial (BOE) | **Sí, en P4** | Es la única capacidad nueva real: obtener de forma reproducible el texto consolidado de un artículo y sus versiones con fecha, y guardar procedencia. Herramientas previstas: `buscar_norma`, `obtener_articulo(norma, art, fecha)`, `versiones(norma, art)`, `diario_del_dia(fecha)`. Fuente: datos abiertos del BOE ⚠️ (endpoints exactos a verificar en la Fase 4). Requiere permitir `www.boe.es` en la red del entorno, porque hoy el proxy lo bloquea. EUR-Lex solo para RGPD y Tratados, como extensión posterior. |
| Base de datos | **No (por ahora)** | La CLI `c1` sobre SQLite cubre todo desde Claude Code. Solo tendría sentido un MCP fino que envuelva la CLI si quieres usar el sistema desde una app sin terminal (Cowork o móvil). Se evalúa en P5. |
| Calendario/planificación | **No crear; reutilizar** | Ya hay un conector de Google Calendar en esta cuenta. Si tu horario de DAW (clases, entregas, exámenes) está ahí, el planificador lo leería en modo solo lectura en P5. Escribir eventos de estudio, solo si lo pides. |
| Estadísticas | **No** | Es cálculo; vive en el motor. |
| Git/GitHub | **No crear** | Git y GitHub ya están integrados; se usan para versionado y auditoría. |
| Búsqueda | **No crear** | La búsqueda web existente basta, restringida a una lista blanca (boe.es, eur-lex.europa.eu, inap.es, funcionpublica.hacienda.gob.es, administracion.gob.es, tribunalconstitucional.es, ministerios). Un resultado fuera de la lista nunca se registra como fuente oficial. |

Resultado: **1 MCP nuevo (BOE) en P4**, más un posible envoltorio de la CLI en P5 si lo usas sin terminal.

---

## FASE 4 — Modelo de datos

### 4.1 Entidades y trazabilidad

```
FUENTE ◀── NORMA_VERSION ◀── NORMA
   ▲            ▲
   │            │ (artículo citado)
BLOQUE ─▶ TEMA ─▶ EPIGRAFE ─▶ CONCEPTO ◀── PREGUNTA ◀── RESPUESTA ─▶ ERROR
                                  ▲    ◀── FLASHCARD      ▲
                                  │                       │
                              ESTADO_CONCEPTO (dominio, SRS)    SESION / SIMULACRO
CAMBIO_NORMATIVO ─▶ ALERTA ─▶ (preguntas/flashcards/epígrafes marcados "revisar")
AUDITORIA: un evento por cada alta, modificación, retirada o decisión
```

Cadena exigida: **Pregunta → concepto → epígrafe → tema → norma/artículo → fuente**. Una pregunta sin `concepto_id` y sin `fuente_id` no puede pasar de `borrador`.

### 4.2 Identificadores

| Entidad | Formato | Ejemplo |
|---|---|---|
| Bloque / tema | `B{n}` / `B{n}-T{nn}` | `B3-T03` |
| Epígrafe | `B{n}-T{nn}-E{x.y}` (numeración del PDF) | `B3-T03-E2.1` |
| Concepto | `CON-{nnnnn}` | `CON-00412` |
| Pregunta | `Q-{nnnnnn}` (+ versión `@v2`) | `Q-000731@v2` |
| Flashcard | `FC-{nnnnn}` | `FC-00088` |
| Respuesta / error | `RSP-{nnnnnn}` / `ERR-{nnnnnn}` | `ERR-001245` |
| Fuente | `SRC-{tipo}-{nnnn}` | `SRC-BOE-0007` |
| Norma | ID BOE cuando exista | `BOE-A-2015-10565` |
| Simulacro / sesión | `SIM-{aaaammdd}-{n}` / `SES-{aaaammdd}-{n}` | `SIM-20261012-1` |

### 4.3 Tablas principales (resumen)

- **bloque**(id, nombre) · **tema**(id, bloque_id, numero, titulo_oficial, fuente_programa_id)
- **epigrafe**(id, tema_id, padre_id, numero, titulo, fuente_id, pagina_ini, pagina_fin)
- **concepto**(id, epigrafe_id, nombre, tipo[definición|plazo|órgano|competencia|mayoría|procedimiento|excepción|requisito|fecha|lista], modo[memorizar|comprender], importancia[A|B|C], examinabilidad[🔴🟠🟡⚪], cita_textual, fuente_id, pagina)
- **concepto_relacion**(origen, destino, tipo[depende_de|se_confunde_con|contrasta_con])
- **fuente**(id, tipo[temario_pdf|boe|eurlex|oficial|resumen_propio], titulo, url_o_ruta, hash_sha256, fecha_consulta, fiabilidad)
- **norma**(id, titulo, rango) · **norma_version**(norma_id, articulo, texto, vigente_desde, vigente_hasta, fuente_id, fecha_consulta)
- **pregunta**(id, version, concepto_id, epigrafe_id, tema_id, dificultad[1–4], tipo[literal|plazo|órgano|excepción|negativa|supuesto|adversarial…], enunciado, opciones[4], correcta, explicacion, fuente_id, norma_articulo, fecha_validacion, estado[borrador|en_revision|aprobada|marcada_revision|retirada], origen[generada|importada_chuleta|oficial], informe_calidad)
- **flashcard**(id, version, concepto_id, anverso, reverso, tipo[hueco|inversa|recuerdo_libre|tabla], mnemotecnia, dato_literal, estado, fuente_id)
- **respuesta**(id, pregunta_id@version, sesion_id|simulacro_id, marcada, correcta_bool, confianza[seguro|dudoso|azar], tiempo_ms, fecha)
- **error**(id, respuesta_id, concepto_id, tipo[K|M|C|R|N|A|E|O|S|G|D*], explicacion, estado[abierto|en_repaso|cerrado]) — *D = normativa desactualizada, añadido a tus códigos
- **estado_concepto**(concepto_id, dominio[0–5], estabilidad_dias, dificultad, repeticiones, fallos, ultimo_contacto, proximo_repaso) — derivado de los eventos, nunca editado a mano
- **sesion**(id, inicio, fin, modo, minutos, plan_propuesto, plan_realizado) · **simulacro**(id, alcance, formato, duracion, nota, penalizacion_aplicada, informe)
- **cambio_normativo**(id, norma_id, articulo, version_anterior, version_nueva, fecha_efecto, detectado_el, fuente_id) · **alerta**(id, cambio_id, temas, preguntas, flashcards, accion_recomendada, estado[abierta|revisada|descartada])
- **auditoria**(id, fecha, actor[agente|alumno], accion, entidad, antes, despues, motivo)
- **config**: examen (fecha estimada 2027-05 ⚠️, formato ⚠️), disponibilidad, DAW, políticas.

Versionado (requisito 27): las preguntas, flashcards, normas y conceptos son **inmutables por versión**. Corregir crea `@v2` y retira `@v1` con motivo. Las respuestas antiguas siguen apuntando a la versión que viste. Los eventos (respuestas, errores, cambios) solo se añaden.

### 4.4 Cálculos deterministas

**Clasificación de la respuesta** (requisito 12): `ACIERTO REAL` = correcta + seguro · `ACIERTO POR DUDAS` = correcta + dudoso · `ACIERTO POR AZAR` = correcta + azar · `ERROR` = incorrecta. Antes de corregir se te pedirá una sola tecla de confianza (s/d/a).

**Dominio 0–5 por concepto** (requisito 20, alineado con tu CLAUDE.md §6) 💡:

| Nivel | Condición mínima (evidencia, nunca por leer) |
|---|---|
| 0 | Sin contacto |
| 1 | Visto (teoría o flashcard vista) sin respuestas evaluadas. **Leer nunca sube de 1.** |
| 2 | ≥ 1 acierto real |
| 3 | ≥ 70 % de acierto real en las últimas ≥ 5 respuestas del concepto |
| 4 | ≥ 85 % de acierto real, con alguna pregunta difícil, y un repaso superado ≥ 7 días después |
| 5 | ≥ 90 % y un repaso superado ≥ 30 días después, sin fallos en los últimos 30 días |

Los aciertos por duda o por azar no suben de nivel. Decaimiento: si la retención estimada baja de 0,5, el concepto se muestra "en riesgo" y su nivel efectivo baja uno (mínimo 2) hasta el siguiente acierto. El nivel de un tema es la media de sus conceptos ponderada por importancia.

**SRS por concepto** (requisito 8) 💡, con estabilidad S en días y retención estimada R = e^(−t/S):
- Fallo → S × 0,3 (mínimo 1) · Acierto por azar → S × 0,5 · Acierto por dudas → S × 1,2 · Acierto real → S × (1,8 + 0,15·(10 − dificultad))
- Intervalo = S × importancia (A 0,8 · B 1 · C 1,3) × proximidad del examen, limitado al rango 1–60 días (tus R1–R6), y nunca más allá de la fecha de examen.
- Listas: *Repaso de hoy* (R < 0,7 o vencido) · *Esta semana* · *En riesgo de olvido* (R < 0,5) · *Dominados* (nivel ≥ 4 y R ≥ 0,85) · *Críticos* (importancia A + nivel ≤ 2, o ≥ 3 fallos en 14 días).
- Los coeficientes son iniciales; quedan en `config` y se ajustan con tus datos.

### 4.5 Métricas (ANALYTICS / ERROR_LOG)

Porcentaje de acierto real, de acierto con dudas, por azar y de error; por tema, bloque, concepto, dificultad y tipo de pregunta; tiempo medio por pregunta; errores recurrentes (mismo concepto ≥ 2 veces en 14 días); evolución semanal; tendencia entre simulacros comparables (mismo formato y alcance). La "nota de dominio" siempre se calcula sobre acierto real, no sobre acierto bruto.

---

## FASE 5 — Flujos de estudio

### 5.1 "Quiero estudiar" / `/hoy`
1. `c1 estado` → progreso, repasos vencidos, errores de los últimos 14 días, temas prioritarios, deuda.
2. `c1 recomendar --minutos N` → reparto (si no dices tiempo, usa el presupuesto del día del plan semanal).
3. El tutor redacta, por ejemplo para 60 min: 10 repaso de errores · 20 teoría del tema siguiente en orden · 15 test · 10 corrección · 5 flashcards.
4. Al terminar: `c1 cerrar-sesion` registra lo realizado frente a lo propuesto.

### 5.2 Ciclo de test (`/test`, `/test-dificil`)
Selección (`c1` prioriza conceptos débiles o vencidos, evita los ya dominados y equilibra dificultad 15/45/30/10) → si faltan preguntas aprobadas: TEST_AGENT genera → QUALITY revisa → solo las `aprobada` entran → se presentan sin pistas → tú respondes letra + confianza → CORRECTION explica cada pregunta (correctas incluidas si fueron por duda o azar) y propone el tipo de error → `c1` registra, actualiza dominio y SRS → resumen con decisión del preparador.

### 5.3 Ingesta del temario (`/revisar-temario`)
PDF subido → hash y registro como `FUENTE` → extracción de texto con páginas → TEMARIO propone el árbol de epígrafes y conceptos **con cita y página** → tú validas el índice (una vez por tema) → se generan fichas y preguntas → QUALITY → banco. Si el tema ya tenía resumen o preguntas importadas, se comparan y las discrepancias quedan como alerta, nunca como sobrescritura.

### 5.4 Duda (`"¿cuál es el plazo?"`, `/explicar artículo 24`)
Identificar concepto → localizar en temario (tema, epígrafe, página) → si es sensible a cambios (plazo, órgano, mayoría…) y la norma no se verificó hace poco, consultar BOE → responder separando **[TEMARIO]**, **[VIGENTE · BOE, fecha de consulta]** y **[EXPLICACIÓN]** → crear flashcard si la importancia es A → registrar la duda como laguna si procede. Si no se localiza en ninguna fuente: "Información no verificada" y no se responde con datos.

### 5.5 Legislación (`/legislacion`, `/cambios`, "¿ha cambiado algo del tema 8?")
Normas del tema 8 por trazabilidad → versión registrada frente a versión vigente en BOE → por cada diferencia: qué cambió, desde cuándo, qué epígrafes afecta, qué preguntas y flashcards quedan `marcada_revision`, qué estudiar de nuevo → alerta "CAMBIO NORMATIVO DETECTADO". Nada se edita hasta que tú lo apruebes; la nueva versión se crea como `@v2` y la antigua queda en el historial.

### 5.6 Planificación (`/plan-semanal`) con prioridad DAW
- Datos de entrada: tu disponibilidad (10–15 h/sem según el perfil), semanas críticas de DAW (entregas, exámenes, proyecto final) y la fecha de examen estimada.
- Regla dura 💡: el presupuesto C1 = mínimo entre tu disponibilidad declarada y el tope DAW. En semana normal, 10 h por defecto (15 h solo si lo dices). En **semana crítica de DAW, modo mantenimiento: máximo 4–5 h**, solo repasos y errores, sin temas nuevos. Ciberseguridad no recibe horas del sistema.
- Salida: Prioridad 1 · Prioridad 2 · Repaso · Test · Simulacro (si procede) · Contenido aplazable · Riesgo principal de la semana.
- Las cifras de horas son propuesta ⚠️: las fijas tú.

### 5.7 Simulacro (`/simulacro [completo|bloque|tema|errores|difícil|aleatorio|legislación]`)
Comprobación previa de preparación ("¿estoy preparado?" = cobertura del alcance con nivel ≥ 2 y sin deuda crítica; si no, se dice por qué) → composición proporcional al alcance con preguntas aprobadas no vistas recientemente → cronómetro → puntuación con el formato configurado ⚠️ (penalización por error solo cuando se verifique la convocatoria) → informe: qué fallaste, por qué (tipos de error), qué estudiar, qué repasar, conceptos aún débiles y comparación con simulacros comparables.

### 5.8 Comandos → agente

| Comando | Agente principal |
|---|---|
| `/hoy`, `/progreso`, `/debilidades` | ORCHESTRATOR (+ ANALYTICS) |
| `/plan-semanal` | STUDY_PLANNER |
| `/test`, `/test-dificil` | TEST (+ ADVERSARIAL) → CORRECTION |
| `/repaso`, `/flashcards`, `/memorizacion` | SPACED_REPETITION + MEMORY |
| `/errores` | ERROR_LOG → TEST (sobre los errores) |
| `/simulacro` | MOCK_EXAM |
| `/tema 7`, `/explicar artículo 24` | TEMARIO + TEACHER |
| `/legislacion`, `/cambios` | LEGISLATION + SYLLABUS_UPDATE |
| `/estadisticas` | ANALYTICS |
| `/revisar-temario` | TEMARIO + QUALITY |

Se mantienen como alias tus comandos actuales (`EMPEZAMOS`, `ESTADO`, `MODO TEST`, `DAME CAÑA`, `continua`…). Los diez modos del punto 22 son estos mismos flujos con distintos parámetros.

### 5.9 Dashboard
💡 Página única (Artifact privado en claude.ai) generada desde los datos, sin gráficos decorativos: progreso general, por bloque y por tema; temas débiles; errores recurrentes; repasos pendientes; próximo simulacro; últimos resultados; tiempo estudiado; histórico; alertas legislativas abiertas. Alternativa: que `chuleta-c1` lea la exportación JSON. Es buena práctica de DAW, pero solo si te interesa y sin quitarle tiempo a DAW.

---

## FASE 6 — Plan de implementación (incremental; cada fase deja el sistema usable)

| Fase | Contenido | Resultado usable al terminar | Depende de ti |
|---|---|---|---|
| **F0 · Cimientos y migración** | Estructura del repo, esquema, CLI `c1`, `c1 build`; importar el mapa de 45 temas (títulos de `00_SEGUIMIENTO.md`), tu estado anterior y el banco chuleta-c1 (500 preguntas y 165 flashcards) como `importada · en_revision`, con opciones rebarajadas; `CLAUDE.md` del repo con tus reglas | `/progreso` responde con tus datos reales (y dice "sin evidencia" donde no la hay) | Aprobar D1; confirmar qué pasó con el Bloque IV |
| **F1 · P1: Temario + Test + Corrección + Errores + Progreso** | Ingesta de PDFs con trazabilidad por página; TEST + QUALITY; CORRECTION con confianza y tipos de error; ERROR_LOG; dominio 0–5; TEACHER básico (`/tema`, `/explicar`) | Haces tests reales, se corrigen con explicación y se guardan errores y progreso | **Subir los PDFs del temario** (al menos los temas ya estudiados) |
| **F2 · P2: Repaso + Flashcards + Planificador** | SRS por concepto (con la regla D2), MEMORY, PLANNER con tope DAW, `/hoy`, `/repaso`, `/plan-semanal` | El sistema propone sesiones y semanas sostenibles | Datos de carga DAW |
| **F3 · P3: Simulacros + Estadísticas + Dashboard** | MOCK_EXAM, ANALYTICS, ADVERSARIAL, dashboard | Simulacros con informe y panel de seguimiento | Formato oficial (se intenta verificar en BOE-A-2025-26262, Anexo III) |
| **F4 · P4: Legislación + cambios** | MCP BOE, registro de normas y versiones, comparación con el temario, alertas, `/legislacion`, `/cambios` | "¿Ha cambiado algo del tema 8?" con fuente y fecha | Permitir `www.boe.es` en la red del entorno |
| **F5 · P5: Automatizaciones** | Rutina semanal (revisión BOE de las normas registradas y plan semanal), lectura del calendario DAW, envoltorio MCP si lo usas sin terminal | El sistema se mantiene solo | Decidir qué automatizar |

Cada fase se entrega en un PR al repo privado con sus tests en verde, y no se pasa a la siguiente sin tu visto bueno.

---

## FASE 7 — Tests (requisito 28)

`pytest` sobre el motor, más casos "golden" para los agentes LLM (entradas fijas con comprobación de salida estructurada). Ninguna fase se da por terminada con tests en rojo.

| Área | Casos mínimos |
|---|---|
| Trazabilidad | Toda pregunta `aprobada` resuelve la cadena pregunta→concepto→epígrafe→tema→fuente; una pregunta sin fuente no puede pasar de `borrador`; `/explicar artículo X` devuelve tema, epígrafe y página exactos o "Información no verificada" |
| Generación de preguntas | 4 opciones distintas y 1 correcta; posiciones equilibradas (ninguna letra > 35 % en 100 preguntas); dificultad dentro de ±10 % del objetivo; duplicados detectados |
| Calidad | Clave contrastada con BOE (interino, 9/18) registrada como verificación; dos claves distintas para un mismo enunciado → QUALITY lo detecta y bloquea; fixture con dos opciones defendibles → rechazada; fuente inventada → rechazada |
| Corrección | Error, acierto real, por dudas y por azar se clasifican bien; tipo de error asignado y guardado; una pregunta anulable no penaliza |
| Detección de errores | "4 fallos del concepto en 14 días" se detecta; ranking de los 10 errores más frecuentes; tema 48 % priorizado sobre 61 % y 87 % |
| Progreso | Leer nunca sube de 1; acierto por azar no sube; el 5 exige repaso superado a ≥ 30 días; decaimiento por tiempo |
| Repetición espaciada | Fallo acorta, acierto real alarga, importancia A acorta, intervalo nunca supera la fecha de examen; con la regla D2 no se generan "toca el tema X" por fecha |
| Simulacros | Composición proporcional al alcance; sin preguntas `marcada_revision`; nota con y sin penalización; comparación solo entre simulacros comparables |
| Planificación | En semana crítica DAW el presupuesto C1 ≤ tope; nunca más horas de las declaradas; ciberseguridad 0 h; existe sección "aplazable" |
| Actualización normativa | Un cambio simulado en un artículo marca sus preguntas y flashcards `marcada_revision`, crea alerta y **no modifica** ningún contenido; la versión anterior sigue en el historial |
| Versionado y auditoría | Editar una pregunta crea `@v2`; las respuestas antiguas siguen apuntando a `@v1`; toda modificación deja evento en `auditoria` |
| Anti-alucinación | Pregunta por un artículo inexistente → "Información no verificada"; conflicto temario/BOE → "Existe una discrepancia entre fuentes"; ninguna métrica aparece en una respuesta si no sale de `c1` |

---

## Decisiones y material que necesito

| # | Pregunta | Recomendación |
|---|---|---|
| D0 | ¿Apruebas este diseño para empezar por F0? | Sí |
| D1 | ¿Alojamiento en el repo privado `oposiciones-c1-estado`, guardado en el proyecto? | Sí |
| D2 | ¿El SRS sugiere por concepto y la academia sigue mandando en los repasos de tema? | Sí |
| — | Subir los PDFs del temario (BLOQUE I–VI), y si existen `TEMARIO_MAP.md`, `ULTIMA_VUELTA.md`, `resumenes/` y `tests/` | Imprescindible para F1 |
| — | Carga DAW: horas por semana y fechas de entregas o exámenes (o si están en tu Google Calendar) | Necesario para F2 |
| — | ¿Se trabajaron los temas IV T01–T03 de chuleta-c1? | Para F0 |
