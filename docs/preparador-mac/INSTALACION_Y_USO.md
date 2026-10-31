# Instalación y uso

## Requisitos

- macOS y un navegador actualizado.
- Python 3, únicamente si se necesita servir los archivos localmente para resolver restricciones del navegador al leer recursos locales.
- Espacio suficiente para descomprimir la versión completa y su biblioteca de documentos.

## Instalación

1. Descarga el paquete ZIP de la versión elegida.
2. Descomprímelo en una carpeta de usuario, por ejemplo `Documentos/Preparador_C1`.
3. No separes `Preparador_C1.html` de las carpetas de recursos incluidas.
4. Abre el HTML en el navegador.

## Servidor local opcional

Algunos navegadores restringen el acceso a archivos auxiliares cuando una página se abre con el protocolo `file://`. En ese caso:

```bash
cd "/ruta/a/Preparador_C1"
python3 -m http.server 8765
```

Abre `http://localhost:8765/Preparador_C1.html`. El servidor escucha en el equipo local; no hace falta exponer el puerto a Internet. Detén el servidor con `Ctrl+C`.

## Copias de seguridad

- Usa la exportación de datos de la aplicación si está disponible.
- Guarda las copias fuera de la carpeta de trabajo y con fecha en el nombre.
- Comprueba de vez en cuando que puedes importar una copia.
- No subas a GitHub exportaciones con datos personales.

## Problemas habituales

**La búsqueda no encuentra el texto de los documentos.** Comprueba que las carpetas auxiliares siguen en su ubicación y prueba con el servidor local.

**El progreso ha desaparecido.** Revisa que usas el mismo navegador y perfil, y que no se han borrado los datos del sitio. Si no existe una copia exportada, puede que no sea recuperable.

**macOS bloquea el archivo `.command`.** Abre el HTML directamente o utiliza el servidor local desde Terminal. No ejecutes scripts cuyo contenido no hayas revisado.
