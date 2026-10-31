# Pruebas y control de calidad

## Estado

No se afirma que la aplicación haya pasado una suite automatizada completa. Este documento establece comprobaciones manuales mínimas antes de distribuir una versión.

## Lista de comprobación

- [ ] Abrir la aplicación en una versión actual de Safari.
- [ ] Abrir la aplicación en Chrome o Firefox.
- [ ] Confirmar que no aparecen errores de JavaScript en la consola.
- [ ] Comprobar que la navegación por bloques y temas funciona.
- [ ] Comprobar búsqueda por nombre y búsqueda de texto, incluida la ejecución con servidor local.
- [ ] Crear una entrada de progreso, recargar la página y confirmar su persistencia.
- [ ] Si hay exportación/importación, exportar, limpiar datos de prueba e importar el archivo.
- [ ] Probar ventanas estrechas y ampliación de texto.
- [ ] Navegar con teclado y revisar foco visible, etiquetas y contraste.
- [ ] Verificar que el paquete contiene las carpetas necesarias y que los enlaces relativos funcionan.
- [ ] Revisar que no se incluyen secretos, datos personales ni material de terceros sin permiso.
- [ ] Confirmar la versión y la fecha en el registro de cambios.

## Regresión

Repite la lista después de modificar el HTML, el catálogo, el índice de texto o el empaquetado. Registra los fallos reproducibles con pasos, navegador y resultado esperado/obtenido.

## Criterio de publicación

No marcar una prueba como superada sin ejecutarla. Si una prueba no se ha realizado, debe permanecer pendiente; si falla, documentar el fallo y no presentarla como resuelta.
