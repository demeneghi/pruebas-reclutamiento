# Cómo agregar una prueba nueva

1. Crea `pruebas/<nombre-en-minusculas-con-guiones>/` con la misma estructura que `pruebas/razonamiento-forma-b/`: `CLAUDE.md`, `src/`, `datos/`, `fuentes/`, `docs/` y `tests/`.
2. Guarda el material original sin modificar en `fuentes/`.
3. Antes de programar, revisa cada reactivo contra `integridad-psicometrica.md` y documenta las correcciones en `docs/correcciones-reactivos.md`.
4. Define y documenta en `docs/decisiones.md`: factores, reglas de calificación, tiempos por serie y modalidades.
5. Escribe `src/config.js` con lo propio de la prueba, tomando como modelo el de razonamiento-forma-b: nombre, carpeta, claves, modalidades, series, bienvenida y secciones del prompt. El motor común (`motor/`) aporta persistencia, flujo, calificación y prompt. Si la prueba necesita un tipo de respuesta que el motor no tiene, agrégalo en `motor/` sin cambiar el comportamiento de los existentes. Genera `src/prueba.html` con `python herramientas/construir.py`.
6. Usa un `CLAVE_BASE` propio en `config.js` para que las pruebas no compartan estado en localStorage.
7. Escribe las pruebas automatizadas de `pruebas-automatizadas.md`.
8. Agrega la prueba al índice del `CLAUDE.md` raíz y del `README.md`.
9. La aplicación generada se llama `src/prueba.html`: así el workflow de Pages la publica sola en `<nombre>/`. `CARPETA` en `config.js` debe ser el nombre de la carpeta; el script de construcción lo comprueba.
10. Agrega su tarjeta al menú de `sitio/index.html`: enlace `<nombre>/`, claves principal y de respaldo en `data-claves`, clave del historial en `data-historial`, partes y duración por modalidad. `sitio/tests/test_selector.py` falla si una prueba publicada no está en el menú.
