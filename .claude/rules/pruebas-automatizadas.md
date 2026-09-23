---
paths:
  - "pruebas/**/src/**"
  - "pruebas/**/tests/**"
  - "pruebas/**/datos/**"
  - "motor/**"
  - "herramientas/**"
---

# Pruebas automatizadas

- Cada prueba psicométrica tiene en `tests/` al menos dos pruebas de extremo a extremo con Playwright en viewport de teléfono:
  - Flujo completo: contesta todos los reactivos con la clave, exige que cada pregunta avance y el puntaje máximo.
  - Persistencia: recarga a mitad de serie (respuesta y reloj conservados), copia principal dañada, dos pestañas, historial y cancelación del aplicador.
- Un cambio en `src/` o `datos/` no se da por terminado mientras esas pruebas fallen. Un cambio en `motor/` afecta a todas las pruebas: corre las de todas.
- `python herramientas/construir.py --verificar` debe pasar: `src/prueba.html` es exactamente lo que genera el script. El workflow `pruebas.yml` lo revisa en cada PR junto con todas las pruebas.
- Las pruebas leen la clave de `datos/clave.json`; si el HTML y los datos divergen, la prueba debe fallar.
- Las esperas de la aplicación (avance automático, pulsaciones largas, tiempos por reactivo) se simulan con el reloj de Playwright (`reloj()` y `esperar()` de `tests/comun.py`), no con pausas reales. Las pausas reales solo para eventos del navegador, como la recarga o la comunicación entre pestañas.
- `python herramientas/probar.py` corre la verificación y todas las pruebas en paralelo; es lo que corre el workflow `pruebas.yml`.
