---
paths:
  - "pruebas/**/src/**"
---

# Experiencia de aplicación

## Formato

- Cada prueba es un solo HTML autocontenido que funciona sin red: CSS, JS, fuentes (base64) y datos incrustados. Sin CDNs ni recursos remotos.
- Diseñada primero para teléfono y tablet: una pregunta por pantalla, objetivos táctiles de al menos 56 px, texto base de 18 a 20 px.
- Tipografía Atkinson Hyperlegible. Estética de hoja de respuestas: fondo de cuadrícula tenue, burbujas que se rellenan, acento amarillo lápiz. Solo modo claro (`color-scheme: light only`).
- Encabezado de marca "Amador Russell, Reclutamiento y selección" en las pantallas del aplicador, bienvenida, final y resultados.
- Lenguaje llano, en tuteo, pensado para candidatos con escolaridad básica. Nada de jerga en instrucciones ni opciones.

## Flujo obligatorio

1. Pantalla del aplicador con datos del candidato, tipo de puesto obligatorio y modalidad de tiempo.
2. Bienvenida del candidato con reglas claras (partes, ejemplos, tiempo, no regresar a partes cerradas).
3. Por serie: introducción con ejemplo interactivo que no cuenta, preguntas, revisión con cuadrícula y cierre confirmado.
4. Pantalla final sin resultados; los resultados solo se abren con pulsación larga del aplicador.

## Respuesta

- Selección única y opciones binarias avanzan solas tras una pausa breve (alrededor de 320 ms) para que se vea la marca.
- Selección múltiple con número fijo avanza sola al completar la cantidad pedida, con pausa mayor y cancelable si se desmarca.
- Respuestas numéricas usan teclado propio en pantalla con botón "Listo" que avanza; nunca el teclado del sistema.
- Siempre existen Anterior, Siguiente y una vista de todas las preguntas dentro de la serie abierta.
