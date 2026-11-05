# Sistema de preparación C1 · Administrativo del Estado

Sistema personal de preparación de MRABEH para el Cuerpo General Administrativo de la Administración del Estado (C1).
Diseño aprobado el 07/10/2026: `docs/DISENO_SISTEMA_C1.md`. Fase actual: **F1 (temario, test, corrección y errores)**.

## Principio rector

**El modelo redacta, explica y clasifica; el motor `c1` cuenta, programa, valida y deja rastro.**
Ninguna estadística, nivel de dominio, fecha de repaso o porcentaje se escribe de memoria: sale de `python3 -m c1 ...`.
Si un dato no está en `data/`, no existe para el sistema: dilo.

## Reglas que no se rompen

1. **No inventar** artículos, plazos, órganos, mayorías, fechas, procedimientos ni normativa.
   Sin fuente: «Información no verificada.» Fuentes en conflicto: «Existe una discrepancia entre fuentes.»
   Temario frente a norma vigente: «El temario puede estar desactualizado respecto a la normativa vigente.»
2. **Separar siempre la procedencia** de lo que se afirma: `[TEMARIO]` (PDF de la academia, con tema/epígrafe/página),
   `[VIGENTE · BOE, fecha de consulta]`, `[EXPLICACIÓN]` (pedagógica). Una inferencia nunca se presenta como hecho jurídico.
3. **Fuentes oficiales primero**: BOE > EUR-Lex > Administraciones y organismos oficiales (INAP, Función Pública, TC).
   Una web secundaria nunca es autoridad si existe la oficial. Guarda URL y fecha de consulta.
4. **Nada se sobrescribe en silencio.** Toda escritura pasa por `c1` (que audita en `data/eventos/auditoria.jsonl`).
   Corregir una pregunta crea una versión nueva; la anterior se conserva. Un cambio normativo marca contenido para revisión, no lo edita.
5. **Una pregunta solo es `aprobada`** si tiene concepto, epígrafe, explicación, fuente, dificultad y fecha de validación,
   y ha pasado la revisión de calidad. Las importadas de chuleta-c1 están `en_revision`: se pueden practicar, pero sus
   resultados no deben venderse como validados.
6. **Ninguna pregunta generada se presenta como oficial.**
7. **Dominio basado en evidencia**: leer nunca sube de 1; aciertos por duda o por azar no suben de nivel; el 5 exige un repaso
   superado al menos 30 días después.

## Prioridades del alumno

1. **DAW** (terminar el ciclo) · 2. C1 · 3. ciberseguridad en segundo plano.
Nunca propongas carga de C1 que perjudique DAW. Disponibilidad declarada: 10–15 h/semana. Examen estimado: mayo de 2027 (no oficial).

## Decisiones vigentes

- **D2 · Repasos**: la academia marca los repasos de tema. El sistema solo sugiere a nivel de concepto;
  no digas «hoy toca el tema X» por fecha.
- El alumno prefiere avanzar por orden dentro de cada bloque y que se le pregunte antes de procesar lotes grandes de material nuevo.
- Se mantienen sus códigos de error: K desconocimiento · M olvido · C confusión · R lectura · N número/plazo/mayoría ·
  A artículo · E excepción · O órgano/competencia · S estrategia · G adivinación · D normativa desactualizada.

## Motor `c1`

```
python3 -m c1 progreso        # alias: estado. Informe con datos reales (--json para máquina)
python3 -m c1 validar         # comprobaciones duras del banco (código de salida 1 si hay errores)
python3 -m c1 alertas         # alertas normativas o de calidad
python3 -m c1 auditoria -n 20 # últimos eventos
python3 -m c1 build           # índice SQLite en build/c1.db (derivado; no se versiona)
python3 -m c1 temario B1-T05  # índice del PDF con páginas y normas de referencia
python3 -m c1 buscar "art. 99" [--tema B1-T05]   # localiza en el temario: tema, epígrafe, página
python3 -m c1 test --tema B1-T05 -n 20 [--modo errores] [--json]
python3 -m c1 corregir SES-... "1a 2b? 3c* 4-"   # sin marca=seguro, ?=dudas, *=azar, -=en blanco
python3 -m c1 clasificar-error ERR-... --tipo C --explicacion "..." --concepto "..."
python3 -m c1 errores [--dias 14]
python3 -m unittest discover -s tests -t .
```

## Datos (`data/`, fuente de verdad, versionada en Git)

| Ruta | Contenido |
|---|---|
| `programa.json` | 6 bloques, 45 temas (`B{n}-T{nn}`), títulos pendientes de cotejar con la convocatoria |
| `estado_declarado.json` | Estado del sistema anterior a 30/08/2026 (declaración, no evidencia) |
| `fuentes.json` | Fuentes registradas con hash |
| `preguntas/<tema>.json`, `flashcards/<tema>.json` | Banco versionado (`Q-nnnnnn`, `FC-nnnnn`) |
| `resumenes/<tema>.md` | Resúmenes de chuleta-c1 (material secundario, no es el temario) |
| `normas/verificaciones.json` | Verificaciones contra BOE |
| `temario/<tema>.json` | Índice de epígrafes (con página) y normas de referencia del PDF; `extraido_automaticamente` hasta que el alumno lo valide |
| `temario/texto/<tema>.jsonl` | Texto del PDF por página, para citar tema y página exactos |
| `eventos/*.jsonl` | Auditoría, sesiones, respuestas, errores, alertas: solo se añade |
| `config.json` | Parámetros (examen, disponibilidad, DAW, política de repasos) |

`legacy/sistema_anterior/` conserva los archivos originales del sistema Markdown anterior como referencia histórica.

## Comandos para el alumno

`/progreso`, `/test [tema] [n] [errores]`, `/errores`, `/tema <tema>`, `/explicar <artículo o concepto>`.
Tras cada test corregido, haz commit y push de `data/`: es la única forma de que el progreso persista.

## Alcance

El CLAUDE.md del sistema anterior (15/09/2026) pedía no convertir la preparación en un proyecto de programación.
El alumno pidió este sistema expresamente el 05/10/2026: se construye solo lo aprobado, fase a fase, sin ampliar otras herramientas.

## Pendiente de recibir del alumno

- PDFs del temario: cargados Bloque I completo y Bloque II T03 (12/45). Faltan Bloque II T01, T02, T04 y los Bloques III–VI.
- Carga DAW (horas y semanas críticas): para la Fase 2.
