# Decisiones de Razonamiento con Figuras, Forma A

## Origen y derechos

- Prueba no verbal del tipo de las matrices progresivas, diseñada para la empresa. El formato general (completar un dibujo o una matriz eligiendo entre figuras) y los tipos de regla son ideas de dominio común en la investigación psicométrica; las figuras, las reglas concretas de cada reactivo y los distractores son propios.
- Los tipos de regla siguen la clasificación de Carpenter, Just y Shell (1990) para problemas de matrices: progresión cuantitativa, distribución de tres valores y suma o resta de figuras, más la analogía de 2 x 2 y la continuación de un patrón.
- No se calcó, vectorizó ni adaptó ninguna lámina del Test de Matrices Progresivas de J. C. Raven. El repositorio es público y no contiene escaneos, capturas ni la clave de ese cuadernillo, que tiene derechos vigentes.
- No hay cuadernillo externo: la fuente es `fuentes/generar_reactivos.py`, que define cada reactivo por su regla y lo dibuja en SVG.

## Series

| Serie | Nombre | Factor | Tipo de reactivo | Opciones |
|---|---|---|---|---|
| A | Completar el dibujo | Percepción de patrones | Dibujo continuo con un hueco cuadrado; la pieza correcta es la región del hueco | 6 |
| B | Analogías de 2 x 2 | Analogía | Un cambio de izquierda a derecha y otro de arriba abajo; los dos cambios conmutan | 6 |
| C | Progresiones de 3 x 3 | Progresión | Cantidad, tamaño, giro, número de lados o posición avanzan paso a paso | 8 |
| D | Distribución de tres | Distribución | Cuadrado latino: cada fila y cada columna tienen un valor de cada tipo, en uno o más atributos | 8 |
| E | Combinación de trazos | Combinación de figuras | La tercera casilla de cada fila junta, resta, deja lo no repetido o deja lo común de las dos primeras | 8 |

12 reactivos por serie, 60 en total. La dificultad crece dentro de cada serie (más atributos que cambian a la vez, reglas menos evidentes) y de una serie a la siguiente. La regla de cada reactivo está en `datos/descripciones.json` y aparece en el prompt.

## Respuesta única y distractores

- Series B, C y D: las opciones son todas las combinaciones de 2 o 3 atributos, cada uno con su valor correcto o uno incorrecto (6 = 2 x 3 y 8 = 2 x 2 x 2), con el mismo principio del conjunto I-RAVEN. Solo una opción tiene todos los valores correctos, y cada valor aparece igual de seguido entre las opciones: elegir el rasgo que más se repite no delata la respuesta. Los valores incorrectos se toman de otras casillas de la matriz para que sean verosímiles.
- En D los atributos siguen cuadrados latinos de orden 3, así que la fila y la columna predicen el mismo valor faltante.
- Serie E: el generador prueba todas las reglas de trazos (suma, resta en ambos sentidos, diferencia, parte común y distribución), por filas y por columnas. Toda regla que explique las filas o columnas completas debe predecir la misma respuesta; si no, busca otra matriz con la misma semilla. Los distractores cambian 1, 2 o 3 de tres trazos elegidos, así que cada trazo está en la mitad de las opciones.
- Serie A: la pieza correcta es exactamente la región del hueco. Los distractores son la misma textura girada, volteada o tomada de otra parte del dibujo, otra textura o la pieza vacía.
- `tests/test_reactivos.py` dibuja cada opción y exige que, en cualquier par de opciones del mismo reactivo, al menos 8 % de la tinta sea distinta. El umbral se calibró revisando a ojo los pares más parecidos (un punto de más, un círculo frente a un pentágono chico); un duplicado da 0 %.
- Revisión visual completa de los 60 reactivos antes de publicarlos; los cambios que salieron de ella están en `correcciones-reactivos.md`.

## Posición de la respuesta

- Semilla fija 20260923 en `fuentes/generar_reactivos.py`. El orden de reactivos y opciones es igual para todos los candidatos.
- Series A y B (24 reactivos, 6 opciones): cada posición 4 veces. Series C, D y E (36 reactivos, 8 opciones): posiciones 1 a 4 cinco veces y 5 a 8 cuatro veces. Nunca la misma posición en dos reactivos seguidos.

## Calificación

| Serie | Factor | Regla | Máximo |
|---|---|---|---|
| A | Percepción de patrones | 1 punto por acierto | 12 |
| B | Analogía | 1 punto por acierto | 12 |
| C | Progresión | 1 punto por acierto | 12 |
| D | Distribución | 1 punto por acierto | 12 |
| E | Combinación de figuras | 1 punto por acierto | 12 |
| Total | | | 60 |

- Sin corrección por azar, como es usual en las pruebas de matrices. El prompt informa el azar esperado: unos 8.5 aciertos contestando todo al azar.
- Escala provisional por porcentaje del máximo, igual a la de Forma B: 90 a 100 Superior, 75 a 89 Superior al promedio, 50 a 74 Promedio, 25 a 49 Inferior al promedio, 0 a 24 Deficiente. Interna y sin baremo; el prompt prohíbe convertir a CI o usar baremos de pruebas publicadas.

## Tiempos

| Serie | Estándar | Extendida (1.25) |
|---|---|---|
| A | 4 min 10 s | 5 min 10 s |
| B | 5 min 10 s | 6 min 30 s |
| C | 8 min 10 s | 10 min 10 s |
| D | 9 min 10 s | 11 min 30 s |
| E | 10 min 10 s | 12 min 40 s |
| Total | 36 min 50 s | 46 min |

- Origen: supuesto inicial sin dato propio, de unos 20 s por reactivo en A hasta unos 50 s en E, más 10 s por serie para compensar el avance automático, como en Forma B. Debe calibrarse con la aplicación piloto sin límite.
- Modalidades fijas por tipo de puesto, iguales a Forma B: estándar (administrativo o técnico) y extendida (operativo: campo, empaque, taller o logística).
- El límite aplicado se guarda al iniciar cada serie; recargar no da tiempo extra.

## Respuesta y avance

- Tipo de respuesta `figura` del motor: la matriz (o el dibujo con hueco) arriba y las opciones numeradas del 1 en adelante, en 3 columnas (6 opciones) o 4 (8 opciones). Cada opción mide al menos 56 px de alto en un teléfono de 390 px.
- Avance automático a los 320 ms de elegir, como la selección única. Con teclado físico, las teclas 1 a 8 eligen la opción.
- Cada serie empieza con un ejemplo de práctica (`datos/ejemplos.json`) que marca la respuesta correcta en verde y no cuenta.

## Prompt

- Misma estructura que Forma B. En las respuestas reactivo por reactivo, en lugar del enunciado va la regla del reactivo, y junto a la respuesta y la clave va la descripción en texto de la figura (por ejemplo, "3 rombos negros"), para que la IA pueda analizar el tipo de error.
- Las descripciones van ofuscadas en el HTML (`DESC`), igual que la clave, porque revelan la regla.

## Persistencia

- Claves de localStorage: `rfFormaA.v1`, `rfFormaA.v1.respaldo` y `rfFormaA.v1.historial`. El resto (recarga, respaldo, pestañas, historial, cancelación y sesión del menú) es el del motor común.
