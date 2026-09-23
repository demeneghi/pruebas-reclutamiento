# Cómo agregar una prueba nueva

1. Crea `pruebas/<nombre-en-minusculas-con-guiones>/` con la misma estructura que `pruebas/razonamiento-forma-b/`: `CLAUDE.md`, `src/`, `datos/`, `fuentes/`, `docs/` y `tests/`.
2. Guarda el material original sin modificar en `fuentes/`.
3. Antes de programar, revisa cada reactivo contra `integridad-psicometrica.md` y documenta las correcciones en `docs/correcciones-reactivos.md`.
4. Define y documenta en `docs/decisiones.md`: factores, reglas de calificación, tiempos por serie y modalidades.
5. Reutiliza la aplicación de razonamiento-forma-b como base; conserva su motor de persistencia, flujo y generación de prompt, y cambia solo reactivos, tipos de respuesta y metadatos.
6. Usa claves de localStorage propias de la prueba para que las pruebas no compartan estado.
7. Escribe las pruebas automatizadas de `pruebas-automatizadas.md`.
8. Agrega la prueba al índice del `CLAUDE.md` raíz y del `README.md`.
9. La aplicación se llama `src/prueba.html`: así el workflow de Pages la publica sola en `<nombre>/`. Con dos o más pruebas, cambia `sitio/index.html` de redirección a menú de pruebas.
