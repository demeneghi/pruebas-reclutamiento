# Razonamiento General, Forma B

## Estado

- `src/config.js` tiene lo propio de esta prueba: nombre, carpeta, claves, modalidades, series (`META`), bienvenida y secciones del prompt (`PROMPT`, `reglaTexto`).
- `datos/reactivos.json` y `datos/clave.json` son la fuente de verdad de reactivos y clave.
- `src/prueba.html` se genera con `python herramientas/construir.py` desde `motor/`, `src/config.js`, `datos/` y `marca/`. No se edita a mano.
- Publicada en GitHub Pages: https://demeneghi.github.io/pruebas-reclutamiento/razonamiento-forma-b/. Se despliega sola al cambiar `src/prueba.html` en `main`.
- Publicada como artefacto privado: https://claude.ai/artifact/4hqbR3TMwNPF7cA9rhMTuE. Las descargas usan `claude.use("downloads")` dentro de Claude y un enlace normal fuera.

## Documentos

- `docs/decisiones.md`: diseño, flujo, calificación, tiempos, persistencia y publicación.
- `docs/correcciones-reactivos.md`: cambios frente al cuadernillo de `fuentes/` y su motivo.
- `docs/pendientes.md`: confirmaciones pendientes y siguiente desarrollo (enlace de un solo uso con Supabase).

## Datos clave

- Claves de localStorage: `rgFormaB.v1`, `rgFormaB.v1.respaldo`, `rgFormaB.v1.historial`.
- Modalidades de tiempo: estándar (administrativo o técnico) y extendida, 1.25 veces (operativo). Definidas en `MODES` y `META` de `src/config.js`.
- Semilla de balanceo de posiciones: 20260922.
