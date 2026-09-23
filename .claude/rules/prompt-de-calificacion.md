---
paths:
  - "pruebas/**/src/**"
---

# Prompt de calificación

Cada prueba genera al final un prompt para que una IA califique e interprete. Estructura obligatoria, en este orden:

1. Rol: psicólogo(a) laboral que apoya el reclutamiento de Amador Russell SPR de RL, empresa agrícola productora de piña MD2 en Veracruz, México.
2. Datos de la aplicación: candidato, edad, escolaridad, puesto, tipo de puesto, modalidad de tiempo, rancho o área, aplicador, fecha, duración y estado (terminada o cancelada).
3. Descripción de la prueba con tabla de series, factor, reactivos, regla, máximo y límite realmente aplicado.
4. Reglas de calificación y escala provisional, con la prohibición de convertir a CI o usar baremos externos.
5. Precalificación automática por serie.
6. Respuestas reactivo por reactivo: enunciado con opciones, respuesta, clave y resultado.
7. Tareas: recalcular, nivel global y por factor, patrones (omisiones por tiempo, azar, errores sistemáticos), escolaridad, ajuste al puesto sin suponer funciones y conclusión en tres niveles.
8. Formato de salida y restricciones: no inventar datos, distinguir hechos de inferencias, una línea de que la prueba no basta para contratar, comparar solo dentro de la misma modalidad.

El prompt contiene la clave: se muestra solo al aplicador y se advierte que no se comparta con el candidato.
