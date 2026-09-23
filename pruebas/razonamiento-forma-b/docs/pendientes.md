# Pendientes

## Por confirmar con Chalo

- Ponderación y tiempos de la versión en papel frente a los asumidos en `decisiones.md`.
- Lista de áreas que contrata la empresa (campo, empaque, taller y mantenimiento, logística, administración): la inferí, no fue declarada.
- Reemplazo de VI-18, que quedó ambiguo tras la reescritura. Propuesta: "Una persona con gripe sigue siendo la misma persona" (sí).
- Logotipo y colores oficiales de Amador Russell.

## Siguiente desarrollo: enlace de un solo uso para aplicación remota

Objetivo: que un recluta pueda contestar desde su teléfono con un enlace que solo funcione una vez, sin exponer la clave.

1. Supabase: tabla de invitaciones (token, candidato, tipo de puesto, estado, creada, abierta, vence, id de dispositivo) y tabla de aplicaciones (respuestas por serie, tiempos, estado).
2. Función de servidor que canjea el token de forma atómica y lo amarra al primer dispositivo; recargar en el mismo dispositivo continúa, cualquier otro recibe "enlace ya utilizado".
3. La clave vive solo en el servidor; el navegador recibe reactivos sin clave. La calificación y el prompt se generan en el servidor o en un panel del aplicador.
4. Hora límite de cada serie validada en el servidor.
5. Respuestas enviadas al cerrar cada serie, además del guardado local.
6. Panel mínimo del aplicador: crear invitación, ver estado, copiar prompt.
7. Orden aleatorio de reactivos y opciones por candidato en la modalidad remota, registrado para poder calificar.

Límites que esto no resuelve: capturas de pantalla y ayuda de terceros. Se recomienda una verificación corta presencial para finalistas.

## Mejoras técnicas

- Calibrar tiempos límite y el umbral de respuesta rápida (`RAPIDA_MS`) con una aplicación piloto sin límite a 8 o 10 trabajadores actuales.
- Diseñar una segunda forma equivalente para alternar.
