---
paths:
  - "pruebas/**/src/**"
  - "motor/**"
---

# Persistencia y seguridad

Perder el avance de un candidato invalida la aplicación. Estas reglas no se relajan.

- Cada cambio de respuesta o de estado se guarda al instante en localStorage, se verifica releyéndolo y se duplica en una copia de respaldo.
- Al recargar, la prueba en curso se reanuda sola en la misma pregunta. El candidato nunca ve la pantalla del aplicador a mitad de prueba.
- La hora límite de cada serie se guarda como marca absoluta: recargar no da tiempo extra.
- Si la misma prueba se abre en otra pestaña, la anterior se bloquea.
- Si el guardado falla, aparece un aviso fijo y visible. Si el navegador no permite guardar o es un navegador embebido de otra app, la pantalla del aplicador lo advierte.
- Toda aplicación terminada o cancelada se archiva en el historial del dispositivo. Ninguna acción del flujo normal borra resultados sin archivarlos antes.
- La sesión del candidato del menú (`motor/sesion.js`) sigue las mismas reglas: se guarda al instante, verificada y con respaldo, y al terminar con el candidato se archiva en el historial de candidatos antes de limpiarse.
- Los cambios de estructura del estado son compatibles hacia atrás o se versionan; una prueba en curso con otra versión se archiva y el aplicador decide.
- El candidato no puede cancelar ni ver resultados: esas acciones están detrás de pulsaciones largas del aplicador.
- El repositorio contiene claves de respuestas: es privado. Nunca se suben datos reales de candidatos (nombres, resultados, prompts generados).
