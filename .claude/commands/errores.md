---
description: Registro de errores, temas más débiles y reincidencias
---
Ejecuta `python3 -m c1 errores --json`. Resume en español, sin cifras que no salgan de ahí: temas de peor a mejor según
acierto real, errores por tipo, conceptos fallados 2 o más veces en 14 días («Has fallado X N veces en los últimos 14 días»)
y los 10 errores más frecuentes. Si hay errores sin clasificar, clasifícalos antes con `c1 clasificar-error`.
Si no hay respuestas evaluadas, dilo y propone un `/test`.
