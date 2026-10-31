# Preparador C1 · Administrativo del Estado

Herramientas personales para organizar y preparar la oposición al **Cuerpo General Administrativo de la Administración del Estado (subgrupo C1)**. El repositorio combina un motor de seguimiento en Python, documentación del proyecto y una web estática para planificar las sesiones de estudio.

> **Estado del proyecto:** en desarrollo. La web de estudio y el motor de Python son herramientas de apoyo; no sustituyen la convocatoria oficial, el BOE ni el temario actualizado. Comprueba siempre la normativa y el programa exigido en la convocatoria vigente.

## Qué puedes hacer

### Web de estudio

La aplicación estática se encuentra en [`site/`](site/) y está diseñada para utilizarse desde el navegador.

- Consultar los bloques y sus temas.
- Abrir el modo de estudio desde el botón **Estudiar** de cada tema.
- Seleccionar un PDF de tu propio ordenador y visualizarlo en la página.
- Utilizar un cronómetro durante la sesión.
- Guardar apuntes y respuestas de recuerdo activo por tema.
- Marcar temas como estudiados y consultar el progreso.
- Registrar sesiones de estudio.
- Exportar e importar una copia de seguridad de los datos.

**Privacidad:** los PDF seleccionados se abren localmente en el navegador; la web no los sube al repositorio. El progreso, los apuntes y las sesiones se guardan en el almacenamiento local del navegador. Por eso, los datos no se sincronizan automáticamente entre dispositivos y pueden perderse al borrar los datos del navegador. Exporta una copia de seguridad periódicamente.

La lista de temas es una estructura de trabajo y debe contrastarse con el programa oficial vigente. Los títulos de los archivos de una academia pueden no coincidir exactamente con los epígrafes oficiales.

### Motor de seguimiento en Python

El proyecto incluye un módulo de línea de comandos y pruebas automatizadas.

- Consultar el progreso mediante el comando `python3 -m c1 progreso`.
- Ejecutar las pruebas unitarias con la biblioteca estándar de Python.
- Consultar las decisiones de diseño y las reglas de trabajo del proyecto en la documentación enlazada más abajo.

## Probar la web

Puedes abrir directamente el archivo `site/index.html` en un navegador moderno. Para probarlo mediante un servidor local, desde la raíz del repositorio ejecuta:

```bash
python3 -m http.server 8000 --directory site
```

Después abre [http://localhost:8000](http://localhost:8000).

No hace falta instalar dependencias de JavaScript para esta web estática. Para visualizar un PDF, selecciónalo desde el modo de estudio de su tema.

## Instalar y probar el motor Python

Requisitos: **Python 3.11 o superior**. El motor está diseñado para utilizar la biblioteca estándar de Python, sin instalar paquetes externos para las pruebas básicas.

Desde la raíz del repositorio:

```bash
python3 --version
python3 -m c1 progreso
python3 -m unittest discover -s tests -t .
```

Si el comando `python3 -m c1 progreso` no encuentra el módulo, comprueba que estás situado en la raíz del repositorio y que la estructura del paquete `c1` está disponible.

## Publicación en GitHub Pages

La configuración de despliegue está en [`.github/workflows/pages.yml`](.github/workflows/pages.yml). Cuando GitHub Pages esté habilitado y el flujo de GitHub Actions termine correctamente, la dirección prevista será:

**https://marbi8891.github.io/oposiciones-c1-estado/**

Para configurarlo en GitHub:

1. Abre **Settings → Pages** en el repositorio.
2. Selecciona **GitHub Actions** como origen de publicación, si esa opción está disponible.
3. Abre la pestaña **Actions** y comprueba que el flujo de despliegue termina con éxito.
4. Si el repositorio es privado, verifica que tu plan y la configuración de la organización permiten publicar Pages con esa visibilidad.

La URL anterior es la dirección prevista; no implica que la publicación esté disponible hasta que el despliegue finalice correctamente.

## Estructura del repositorio

```text
.
├── .github/workflows/     # Automatizaciones y despliegue
├── c1/                    # Motor Python de seguimiento
├── data/                  # Datos del proyecto y migraciones
├── docs/                  # Diseño y documentación
│   └── preparador-mac/    # Documentación de la aplicación local
├── scripts/               # Scripts auxiliares y migraciones
├── site/                  # Web estática del preparador
├── tests/                 # Pruebas automatizadas
├── CLAUDE.md              # Reglas de trabajo para Claude
└── README.md
```

La estructura concreta puede evolucionar a medida que avance el proyecto.

## Documentación

- [Diseño del sistema C1](docs/DISENO_SISTEMA_C1.md)
- [Reglas de trabajo para Claude](CLAUDE.md)
- [Documentación del Preparador C1 para Mac](docs/preparador-mac/README.md)
- [Instalación y uso](docs/preparador-mac/INSTALACION_Y_USO.md)
- [Funcionalidades y limitaciones](docs/preparador-mac/FUNCIONALIDADES_Y_LIMITACIONES.md)
- [Privacidad y datos](docs/preparador-mac/PRIVACIDAD_Y_DATOS.md)
- [Pruebas y calidad](docs/preparador-mac/PRUEBAS_Y_CALIDAD.md)
- [Contenido y fuentes](docs/preparador-mac/CONTENIDO_Y_FUENTES.md)
- [Hoja de ruta](docs/preparador-mac/HOJA_DE_RUTA.md)
- [Registro de cambios](docs/preparador-mac/CHANGELOG.md)
- [Guía para contribuir](docs/preparador-mac/CONTRIBUIR.md)
- [Seguridad](docs/preparador-mac/SEGURIDAD.md)

## Migración reproducible

La migración de la Fase 0 puede ejecutarse sobre un directorio `data/` vacío indicando el HTML de origen y el commit de referencia:

```bash
python3 scripts/migracion_f0.py <chuleta-c1/index.html> --commit <sha>
```

Sustituye los valores entre `<>` por la ruta del HTML y el SHA correspondiente.

## Alcance y límites

- El proyecto está en desarrollo y puede contener funciones incompletas o cambios pendientes.
- La web no ofrece autenticación ni sincronización en la nube; sus datos se guardan en el navegador.
- La selección de un PDF local no implica que el archivo se distribuya con la web.
- No se debe asumir que el temario, las referencias jurídicas o los títulos de los temas están completamente actualizados sin verificarlos frente a la convocatoria oficial.
- No incluyas contraseñas, tokens, claves privadas ni datos personales sensibles en incidencias, archivos de ejemplo o commits.

## Contribuciones y errores

Antes de proponer cambios, revisa [`CLAUDE.md`](CLAUDE.md), el diseño del sistema y las pruebas existentes. Para cambios en el motor Python, ejecuta la suite de pruebas. No incluyas datos privados ni material protegido por derechos de autor sin autorización.

---

Proyecto personal de preparación y seguimiento del estudio. La información de esta documentación describe el estado de desarrollo del repositorio y no constituye asesoramiento jurídico ni una garantía de cobertura del examen.
