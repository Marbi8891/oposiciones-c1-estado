# Privacidad y datos

## Tratamiento local

La aplicación se ha preparado para un uso personal local en el navegador. Según la versión, el progreso se almacena en el almacenamiento local del navegador. Esto significa que puede desaparecer si se borran los datos, se cambia de perfil o se utiliza otro navegador.

## Recomendaciones

- Exporta periódicamente una copia de tus datos si la función está disponible.
- Guarda las copias en una ubicación privada y protegida.
- No incluyas nombres completos, documentos de identidad, información de salud, credenciales ni otros datos sensibles en archivos que vayas a subir a GitHub.
- No incorpores claves, tokens, contraseñas ni secretos en el código.
- Antes de publicar una versión, revisa el contenido del HTML, los archivos de configuración, los registros y las exportaciones.

## Material de terceros

Los documentos de academias pueden estar sujetos a derechos de autor o a condiciones de uso. La posesión de una copia no implica permiso para redistribuirla. No publiques PDF, extractos extensos ni paquetes con material de terceros sin comprobar que tienes autorización. Mantén privado el repositorio si contiene esos materiales y evita subirlos a Releases.

## Servidor local

Si se usa `python3 -m http.server`, ejecútalo desde la carpeta del proyecto y no configures el equipo para exponer ese servicio a redes públicas. El servidor local se usa para evitar algunas restricciones del navegador al acceder a archivos auxiliares.

## Incidentes

Si detectas una clave o un dato personal en un commit, no basta con borrarlo en una versión posterior: el dato puede seguir presente en el historial. Revoca las credenciales expuestas y limpia el historial siguiendo un procedimiento seguro.
