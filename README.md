# oposiciones-c1-estado

Sistema personal de preparación para Administrativo del Estado (C1), con agentes de Claude y un motor determinista en Python.

- Diseño: [docs/DISENO_SISTEMA_C1.md](docs/DISENO_SISTEMA_C1.md)
- Reglas para Claude: [CLAUDE.md](CLAUDE.md)

```
python3 -m c1 progreso
python3 -m unittest discover -s tests -t .
```

Solo usa la biblioteca estándar de Python 3.11+.
La migración de la Fase 0 es reproducible: `python3 scripts/migracion_f0.py <chuleta-c1/index.html> --commit <sha>` sobre un `data/` vacío.


## Preparador C1 para Mac

Documentación de la aplicación local para macOS: [docs/preparador-mac/README.md](docs/preparador-mac/README.md). Incluye instalación, privacidad, limitaciones, pruebas, fuentes jurídicas y hoja de ruta. La aplicación HTML y el paquete completo todavía deben incorporarse y validarse como una versión distribuible independiente.
