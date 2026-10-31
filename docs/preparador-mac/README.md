# Preparador C1 para Mac

Aplicación personal para organizar el estudio del Cuerpo General Administrativo de la Administración del Estado (subgrupo C1). La interfaz se ejecuta en el navegador y está pensada para uso local en macOS.

> Estado: versión personal en desarrollo. La existencia de la aplicación no implica que el temario esté completo ni que todas las referencias normativas estén verificadas.

## Qué incluye esta entrega

- Aplicación HTML que se abre en un navegador.
- Organización del estudio por bloques y temas, conforme al plan de trabajo incluido en el proyecto.
- Herramientas de seguimiento del estudio y gestión de material según las funciones presentes en la versión distribuida.
- Biblioteca de archivos de estudio e índice de texto en el paquete completo.

La lista exacta de funciones depende de la versión de la aplicación que se distribuya. Consulta `FUNCIONALIDADES_Y_LIMITACIONES.md` antes de depender de una función concreta.

## Inicio rápido en macOS

1. Descarga el ZIP de la versión completa desde **Releases**, si se ha publicado una versión allí.
2. Descomprime el ZIP en una carpeta local.
3. Conserva juntos el HTML y las carpetas de recursos que acompañen al paquete.
4. Abre `Preparador_C1.html` con Safari, Chrome o Firefox.
5. Si la búsqueda de texto no funciona al abrir el HTML directamente, abre Terminal en la carpeta del proyecto y ejecuta:

   ```bash
   python3 -m http.server 8765
   ```

   Después visita `http://localhost:8765/Preparador_C1.html`. Para detener el servidor, vuelve a Terminal y pulsa `Ctrl+C`.

No es una aplicación nativa `.app` ni necesita instalarse como tal.

## Datos y privacidad

La versión local está diseñada para ejecutarse en el navegador. El progreso puede guardarse en el almacenamiento local del navegador; borrar esos datos o cambiar de navegador puede provocar pérdida de información. Haz exportaciones de respaldo cuando la aplicación disponga de esa opción.

No publiques en este repositorio público material de academia, datos personales ni copias de seguridad con información privada. El repositorio debe mantenerse privado mientras contenga material cuyo permiso de redistribución no esté confirmado.

## Documentación

- [Instalación y uso](INSTALACION_Y_USO.md)
- [Funciones y limitaciones](FUNCIONALIDADES_Y_LIMITACIONES.md)
- [Privacidad y datos](PRIVACIDAD_Y_DATOS.md)
- [Pruebas y control de calidad](PRUEBAS_Y_CALIDAD.md)
- [Estado y hoja de ruta](HOJA_DE_RUTA.md)
- [Contenido y verificación jurídica](CONTENIDO_Y_FUENTES.md)
- [Registro de cambios](CHANGELOG.md)

## Alcance y responsabilidad

Esta herramienta organiza el estudio, pero no sustituye la convocatoria oficial, las bases, el BOE ni la comprobación de la normativa vigente. Antes de memorizar fechas, artículos, plazos, órganos o procedimientos, contrástalos con una fuente oficial y con el texto aplicable a la convocatoria.
