# Seguridad

## Alcance

La aplicación está pensada para uso local en el navegador. Esta documentación no equivale a una auditoría de seguridad ni garantiza que el código esté libre de vulnerabilidades.

## Reglas de seguridad

- No almacenar secretos, contraseñas, tokens o claves API en el HTML ni en archivos versionados.
- No ejecutar código de terceros introducido por usuarios sin una sandbox diseñada y probada para ello.
- Tratar como no confiables los archivos importados y los datos pegados por el usuario.
- Evitar insertar contenido no confiable con `innerHTML`; preferir APIs seguras del DOM o sanitizar con una solución revisada.
- Revisar enlaces externos, dependencias y permisos antes de distribuir una versión.
- Mantener el repositorio privado si contiene material de academia o datos cuyo derecho de publicación no esté confirmado.

## Comunicar un problema

No publiques detalles explotables de una vulnerabilidad en un issue público. Utiliza los canales privados de seguridad que permita GitHub para este repositorio. Si no hay un canal privado configurado, contacta con el mantenedor antes de divulgar detalles técnicos.
