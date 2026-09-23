# Razonamiento General, Forma B

## Estado

- `src/prueba.html` es la fuente de verdad: todo incrustado (reactivos, clave ofuscada en base64, fuentes).
- `datos/reactivos.json` y `datos/clave.json` son extracción legible del HTML. Todavía no hay build que los inyecte: si cambias un reactivo, cámbialo en ambos lados. Crear ese build es el primer pendiente técnico.
- Publicada en GitHub Pages: https://demeneghi.github.io/pruebas-reclutamiento/razonamiento-forma-b/. Se despliega sola al cambiar `src/prueba.html` en `main`.
- Publicada como artefacto privado: https://claude.ai/artifact/4hqbR3TMwNPF7cA9rhMTuE. Las descargas usan `claude.use("downloads")` dentro de Claude y un enlace normal fuera.

## Documentos

- `docs/decisiones.md`: diseño, flujo, calificación, tiempos, persistencia y publicación.
- `docs/correcciones-reactivos.md`: cambios frente al cuadernillo de `fuentes/` y su motivo.
- `docs/pendientes.md`: confirmaciones pendientes y siguiente desarrollo (enlace de un solo uso con Supabase).

## Datos clave

- Claves de localStorage: `rgFormaB.v1`, `rgFormaB.v1.respaldo`, `rgFormaB.v1.historial`.
- Modalidades de tiempo: estándar (administrativo o técnico) y extendida, 1.25 veces (operativo). Definidas en `MODES` y `META` del script.
- Semilla de balanceo de posiciones: 20260922.
