# Razonamiento con Figuras, Forma A

## Estado

- Prueba no verbal de 5 series y 60 reactivos del tipo de las matrices progresivas, con figuras y reglas propias. No contiene material del Test de Matrices Progresivas de Raven y no debe contenerlo: el repositorio es público.
- `fuentes/generar_reactivos.py` es la fuente de los reactivos: define cada uno por su regla, lo dibuja en SVG, verifica que tenga una sola respuesta y escribe `datos/reactivos.json`, `clave.json`, `descripciones.json` (regla y figuras en texto para el prompt) y `ejemplos.json`. No edites esos JSON a mano: cambia el generador, córrelo y reconstruye.
- `src/config.js` tiene lo propio de esta prueba: nombre, carpeta, claves, modalidades, series (`META`), bienvenida y secciones del prompt.
- `src/prueba.html` se genera con `python herramientas/construir.py`. No se edita a mano.
- Usa el tipo de respuesta `figura` del motor.

## Comandos

```bash
python pruebas/razonamiento-figuras/fuentes/generar_reactivos.py
python herramientas/construir.py
python pruebas/razonamiento-figuras/tests/test_reactivos.py
```

`test_reactivos.py` falla si los datos no coinciden con el generador o si dos opciones de un reactivo casi no se distinguen.

## Documentos

- `docs/decisiones.md`: origen, series, respuesta única, posiciones, calificación, tiempos y prompt.
- `docs/correcciones-reactivos.md`: cambios que salieron de la revisión de los reactivos generados.
- `docs/pendientes.md`: confirmaciones y calibración con la aplicación piloto.

## Datos clave

- Claves de localStorage: `rfFormaA.v1`, `rfFormaA.v1.respaldo`, `rfFormaA.v1.historial`.
- Modalidades de tiempo: estándar (administrativo o técnico) y extendida, 1.25 veces (operativo).
- Semilla de generación y de balanceo de posiciones: 20260923.
