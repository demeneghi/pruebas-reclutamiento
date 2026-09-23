# Decisiones del proyecto

## Formato y diseño

- Un solo HTML autocontenido para que funcione sin conexión en ranchos. Las fuentes (Atkinson Hyperlegible 400 y 700, subconjunto latino) van incrustadas en base64: distingue bien 0/O y 1/l, útil en series numéricas.
- Metáfora de hoja de respuestas: fondo de cuadrícula tenue, opciones con burbuja que se rellena al elegir, acento amarillo lápiz. Solo modo claro, forzado con `color-scheme: light only`.
- Una pregunta por pantalla, botones de al menos 56 px de alto, tipografía de 18 a 20 px.
- Marca: encabezado de texto "Amador Russell, Reclutamiento y selección". No hay logotipo ni colores corporativos oficiales todavía.

## Flujo

1. Pantalla del aplicador: nombre, edad, escolaridad, puesto, tipo de puesto (obligatorio), rancho o área (opcional), aplicador, con o sin tiempo límite.
2. Bienvenida del candidato.
3. Por cada serie: introducción con ejemplo interactivo que no cuenta, preguntas, revisión con cuadrícula y cierre. Una serie cerrada no se puede reabrir.
4. Pantalla final. Los resultados se abren manteniendo presionado un botón 1.5 s.
5. Resultados: tabla resumen y prompt (copiar, compartir, descargar .txt).

## Respuesta y avance

- Selección única, par mismo/contrario, sí/no, verdadero/falso: avance automático a los 320 ms.
- Serie IV (elegir dos): avance automático 550 ms después de la segunda selección; si desmarca antes, se cancela.
- Series V y X: teclado numérico propio con botón "Listo". En X el botón dice "Siguiente número" en la primera casilla.
- Teclado físico: dígitos, punto, retroceso, Enter y flechas.

## Calificación

| Serie | Factor | Regla | Máximo |
|---|---|---|---|
| I | Información | 1 punto por acierto | 16 |
| II | Juicio | 2 puntos por acierto | 22 |
| III | Vocabulario | aciertos menos errores, mínimo 0 | 25 |
| IV | Síntesis | 1 punto si marca exactamente las 2 correctas | 15 |
| V | Concentración | 2 puntos por acierto | 24 |
| VI | Análisis | aciertos menos errores, mínimo 0 | 20 |
| VII | Abstracción | 1 punto por acierto | 20 |
| VIII | Planeación | 1 punto por acierto | 17 |
| IX | Organización | 1 punto por acierto | 18 |
| X | Atención | 2 puntos si ambos números son correctos | 22 |
| Total | | | 199 |

La ponderación sigue la convención Terman-Merrill según se asumió; falta confirmarla contra la versión en papel. Escala provisional por porcentaje del máximo: 90 a 100 Superior, 75 a 89 Superior al promedio, 50 a 74 Promedio, 25 a 49 Inferior al promedio, 0 a 24 Deficiente.

## Tiempos

- Base Terman usual: 2, 2, 2, 3, 5, 2, 2, 3, 3 y 4 minutos.
- Se sumaron 10 s a las series con avance automático (I, II, III, VI, VII, VIII, IX) para compensar el retraso de la animación.
- Dos modalidades fijas por tipo de puesto: estándar (administrativo o técnico) y extendida, 1.25 veces, redondeada a 10 s (operativo: campo, empaque, taller o logística). Se descartó 1.5 veces por relajar demasiado.
- Modo "Sin límite (piloto)" para calibrar con personal actual.
- El límite aplicado se guarda al iniciar cada serie; recargar no da tiempo extra.

## Persistencia

- localStorage con clave `rgFormaB.v1`, copia idéntica en `rgFormaB.v1.respaldo` y verificación por relectura en cada guardado.
- Al recargar, la prueba en curso se reanuda sola en la misma pregunta. Si la versión de los reactivos cambió (`FORM_ID`), se archiva y el aplicador decide.
- Si la prueba se abre en otra pestaña, la anterior se bloquea.
- Historial de las últimas 30 aplicaciones en `rgFormaB.v1.historial`.
- Menú oculto del aplicador: mantener presionado 3 s el título de la parte para cancelar una aplicación.
- Banner rojo fijo si falla el guardado; aviso si el navegador no permite guardar o si es un navegador embebido de otra app.

## Prompt de calificación

Incluye rol, contexto de la empresa, datos de la aplicación, modalidad y límite real por serie, reglas, escala provisional, precalificación automática, respuestas reactivo por reactivo con clave, tareas, formato de salida y restricciones. Prohíbe convertir a CI y comparar entre modalidades.

## Publicación

- Artefacto privado de Claude. Las descargas usan la capacidad `claude.use("downloads")` y, fuera de Claude, un enlace de descarga normal.
- Alternativas evaluadas: Netlify Drop, Cloudflare Pages y Vercel Drop. Cualquier hosting estático deja la prueba pública y el historial depende del dominio: no cambiar de servicio una vez en uso.
