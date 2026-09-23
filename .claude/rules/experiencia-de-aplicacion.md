---
paths:
  - "pruebas/**/src/**"
  - "motor/**"
---

# Experiencia de aplicación

## Formato

- Cada prueba es un solo HTML con su CSS, JS y datos. Una vez abierta no depende de la red: respuestas, reloj, guardado y prompt funcionan sin conexión.
- `src/prueba.html` se genera con `python herramientas/construir.py` a partir de `motor/` (común a todas las pruebas), `src/config.js` (lo propio de la prueba), `datos/` y `marca/`. Nunca se edita a mano: el cambio va a su fuente y después se reconstruye.
- Fuentes, imágenes y bibliotecas pueden venir de CDN. Las fuentes se cargan sin bloquear la página (`media="print" onload="this.media='all'"` y `display=swap`) para que una red lenta no retrase la prueba; si no cargan, se usa la fuente del sistema. Si la prueba también se publica como artefacto de Claude, usa solo orígenes que el artefacto permita: Google Fonts para fuentes, cdnjs.cloudflare.com o cdn.jsdelivr.net para bibliotecas, e imágenes incrustadas.
- Diseñada primero para teléfono y tablet: una pregunta por pantalla, objetivos táctiles de al menos 56 px, texto base de 18 a 20 px.
- Tipografía Atkinson Hyperlegible. Estética de hoja de respuestas: fondo de cuadrícula tenue, burbujas que se rellenan, acento amarillo lápiz. Solo modo claro (`color-scheme: light only`).
- Encabezado de marca "Amador Russell, Reclutamiento y selección" en las pantallas del aplicador, bienvenida, final y resultados. En la bienvenida, el logotipo animado (`LOGO`, generado desde `marca/`) ocupa el lugar del nombre.
- Animaciones solo decorativas y fuera de las partes con tiempo: breves (menos de 3 s), de una sola vez, sin bloquear botones y desactivadas con `prefers-reduced-motion`.
- Lenguaje llano, en tuteo, pensado para candidatos con escolaridad básica. Nada de jerga en instrucciones ni opciones.

## Flujo obligatorio

1. Menú de pruebas: el aplicador captura una sola vez los datos del candidato, el tipo de puesto (obligatorio) y la modalidad de tiempo. Mientras dure la sesión, el menú muestra siempre el nombre del candidato; durante la prueba no se muestra fuera del saludo.
2. El aplicador elige la prueba. La prueba toma al candidato de la sesión y empieza en la bienvenida, con reglas claras (partes, ejemplos, tiempo, no regresar a partes cerradas).
3. Por serie: introducción con ejemplo interactivo que no cuenta, preguntas, revisión con cuadrícula y cierre confirmado.
4. Pantalla final sin resultados. El aplicador vuelve al menú con pulsación larga y elige la siguiente prueba.
5. Resultados y un solo prompt con todas las pruebas del candidato, en el menú, tras pulsación larga del aplicador.
6. Abierta como archivo suelto o artefacto (sin menú), la prueba conserva su propia pantalla de captura y de resultados.

## Respuesta

- Selección única y opciones binarias avanzan solas tras una pausa breve (alrededor de 320 ms) para que se vea la marca.
- Selección múltiple con número fijo avanza sola al completar la cantidad pedida, con pausa mayor y cancelable si se desmarca.
- Respuestas numéricas usan teclado propio en pantalla con botón "Listo" que avanza; nunca el teclado del sistema.
- Siempre existen Anterior, Siguiente y una vista de todas las preguntas dentro de la serie abierta.
