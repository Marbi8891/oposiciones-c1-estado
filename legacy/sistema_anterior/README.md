# PREPARADOR PRIVADO C1 — CLAUDE

Sistema de preparación profesional para la oposición de Administrativo de la Administración del Estado, subgrupo C1.

## Objetivo

Convertir a Claude en un preparador privado que dirija la preparación completa:

**temario → comprensión → recuerdo → test → corrección → repaso → simulacro → mejora**

No está pensado para limitarse a resumir PDFs.

## Estructura

- `CLAUDE.md` — instrucciones maestras del preparador (léelo tú también una vez; resume cómo funciona el sistema).
- `PERFIL_ALUMNO.md` — contexto estable del opositor.
- `PROGRESO.md` — estado por temas y bloques (sustituye a `00_SEGUIMIENTO.md`).
- `ERROR_LOG.md` — registro de errores.
- `REPASOS.md` — cola de repetición espaciada.
- `TEMARIO_MAP.md` — mapa maestro del programa (45 temas, 6 bloques).
- `SIMULACROS.md` — historial de simulacros.
- `CAMBIOS_LEGISLATIVOS.md` — control de normativa y actualizaciones.
- `SESIONES.md` — diario de sesiones.
- `ULTIMA_VUELTA.md` — cuaderno de alta rentabilidad.
- `CONFIG.yaml` — parámetros de funcionamiento.
- `PROMPT_INICIO.md` — primer mensaje para reactivar el sistema en una sesión nueva.
- `BLOQUE I/` a `BLOQUE VI/` — PDFs originales del temario (ya existentes, no se han movido).
- `resumenes/` — chuletas ya generadas por tema (formato `T0X_resumen.md` o `T0X_Bloque_Y_resumen.md`).
- `tests/` — tests de 20 preguntas ya generados por tema.

## Uso

1. Abre esta carpeta con Claude (Cowork o Claude Code).
2. Si es una sesión nueva, pega el contenido de `PROMPT_INICIO.md`.
3. Usa comandos como:
   - `EMPEZAMOS`
   - `¿QUÉ ESTUDIO HOY?`
   - `MODO TEST`
   - `MODO REPASO`
   - `SIMULACRO`
   - `ESTADO`
   - `DAME CAÑA`
4. No borres los archivos de seguimiento — Claude los actualiza automáticamente al final de cada sesión relevante.

## Migración desde el sistema anterior

Este sistema sustituye a `00_SEGUIMIENTO.md` y `00_PLAN_DE_ESTUDIO.md`. Todo su contenido (9 temas ya estudiados: Bloque I T01-T05, Bloque II T01-T04 completo) se ha volcado en `PROGRESO.md` y `TEMARIO_MAP.md`. Los dos archivos antiguos se conservan como referencia histórica pero ya no se actualizan; puedes borrarlos cuando quieras.

## Regla fundamental

Claude debe leer los archivos de seguimiento antes de planificar cada sesión y actualizarlos al finalizar. El alumno no tiene que gestionar manualmente el algoritmo de estudio: el preparador decide qué toca según rendimiento, vencimiento de repasos, importancia y proximidad al examen.
