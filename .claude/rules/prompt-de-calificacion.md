---
paths:
  - "pruebas/**/src/**"
---

# Prompt de calificación

Cada prueba genera al final un prompt para que una IA califique e interprete. Estructura obligatoria, en este orden:

1. Rol: psicólogo(a) laboral que apoya el reclutamiento de Amador Russell SPR de RL, empresa agrícola productora de piña MD2 en Veracruz, México.
2. Datos de la aplicación: candidato, edad, escolaridad, años desde que dejó la escuela, uso de teléfono o tablet, puesto, tipo de puesto, modalidad de tiempo, rancho o área, aplicador, fecha, duración, estado (terminada o cancelada) e incidencias anotadas por el aplicador.
3. Descripción de la prueba con tabla de series, factor, reactivos, regla, máximo y límite realmente aplicado.
4. Reglas de calificación y escala provisional, con la prohibición de convertir a CI o usar baremos externos.
5. Precalificación automática por serie.
6. Indicadores de proceso por serie, calculados en el código a partir del registro por reactivo: mediana del tiempo de primera respuesta, respuestas rápidas (umbral interno y provisional) y cuántas fueron erróneas, cambios de respuesta clasificados por su efecto, omisiones vistas y no vistas, precisión y porcentaje del límite usado. Si la aplicación no tiene registro, el prompt lo dice.
7. Respuestas reactivo por reactivo: enunciado con opciones, respuesta, clave, resultado, tiempo de primera respuesta y cambios.
8. Tareas: recalcular, nivel global y por factor, patrones (omisiones por tiempo, azar, errores sistemáticos, cambios de respuesta) con tiempos comparados solo dentro de la serie del candidato, escolaridad, condiciones de la aplicación, ajuste al puesto sin suponer funciones y conclusión en tres niveles.
9. Formato de salida y restricciones: no inventar datos, distinguir hechos de inferencias, una línea de que la prueba no basta para contratar, no usar la edad para ajustar, inferir ni concluir, comparar solo dentro de la misma modalidad.

La aplicación registra por reactivo el tiempo en pantalla, el tiempo hasta la primera respuesta, la primera respuesta y los cambios. Los indicadores se calculan en el código, no se piden a la IA.

El prompt contiene la clave: se muestra solo al aplicador y se advierte que no se comparta con el candidato.
