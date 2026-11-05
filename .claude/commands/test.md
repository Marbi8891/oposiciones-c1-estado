---
description: Test en modo evaluado con corrección explicada y registro de errores
argument-hint: "[tema, p. ej. B1-T05] [nº de preguntas] [errores]"
---
Argumentos: $ARGUMENTS

1. Crea el test con `python3 -m c1 test --tema <tema> -n <n> --json` (sin tema: todos; con «errores»: `--modo errores`).
   Por defecto 20 preguntas. Si el alumno dice cuánto tiempo tiene, ajusta n.
2. Muestra las preguntas numeradas con sus opciones a–d, **sin soluciones ni pistas**. Indica una sola vez que el banco
   está en revisión (preguntas importadas sin fuente validada) si alguna lo está.
3. Pide las respuestas en una línea: `1a 2b? 3c* 4-` (sin marca = seguro, `?` = con dudas, `*` = al azar, `-` = en blanco).
4. Corrige con `python3 -m c1 corregir <SES> "<respuestas>" --json`. Las cifras salen de ahí, no las calcules tú.
5. Por cada pregunta fallada, o acertada con dudas o al azar: explica el porqué. Para el fundamento, localiza el dato con
   `python3 -m c1 buscar "<término>" --tema <tema>` y cítalo como `[TEMARIO] tema · p. N · epígrafe`. Si el temario de ese
   tema no está cargado, o no aparece, dilo: «Información no verificada». No inventes artículos ni plazos.
6. Clasifica cada error con `python3 -m c1 clasificar-error ERR-… --tipo <K|M|C|R|N|A|E|O|S|G|D|T> --explicacion "…" --concepto "…"`.
   Usa un nombre de concepto estable y breve (p. ej. «moción de censura: mayoría»), para que las reincidencias se detecten.
7. Cierra con: acierto real frente a acierto bruto, errores por tipo y qué repasar. Recuerda la regla D2: la academia marca
   los repasos de tema.
8. Haz commit de `data/` con un mensaje como «Test SES-… corregido» y súbelo.
