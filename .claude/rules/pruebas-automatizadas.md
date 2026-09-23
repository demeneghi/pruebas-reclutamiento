---
paths:
  - "pruebas/**/src/**"
  - "pruebas/**/tests/**"
  - "pruebas/**/datos/**"
---

# Pruebas automatizadas

- Cada prueba psicométrica tiene en `tests/` al menos dos pruebas de extremo a extremo con Playwright en viewport de teléfono:
  - Flujo completo: contesta todos los reactivos con la clave, exige que cada pregunta avance y el puntaje máximo.
  - Persistencia: recarga a mitad de serie (respuesta y reloj conservados), copia principal dañada, dos pestañas, historial y cancelación del aplicador.
- Un cambio en `src/` o `datos/` no se da por terminado mientras esas pruebas fallen.
- Las pruebas leen la clave de `datos/clave.json`; si el HTML y los datos divergen, la prueba debe fallar.
