# Integridad psicométrica

Aplica a toda prueba del repositorio: contenido, clave, calificación y tiempos.

## Reactivos

- Cada reactivo tiene exactamente una respuesta defendible (o exactamente las que pide la instrucción). Si existe una segunda lectura válida, corrige el reactivo; no lo dejes pasar.
- Revisa en particular: analogías numéricas con dos reglas posibles (suma y producto, cuadrado y múltiplo), deícticos (este, ese, aquel), afirmaciones de opinión presentadas como hechos, excepciones del mundo real en reactivos de "siempre", erratas en oraciones desordenadas y unidades o supuestos implícitos en problemas.
- Toda corrección a un reactivo del cuadernillo fuente se documenta en `docs/correcciones-reactivos.md` de esa prueba con el motivo.
- Balancea la posición de la respuesta correcta entre opciones y la proporción de verdadero y falso o sí y no. Usa una semilla fija y documéntala; el orden es igual para todos los candidatos salvo que la prueba defina aleatorización registrada.
- Opciones numéricas ordenadas conservan su orden natural.

## Clave y calificación

- La clave nunca se muestra al candidato ni aparece legible en el HTML. Si la prueba se aplica a distancia, la clave vive solo en el servidor.
- Las reglas de calificación se declaran explícitas por serie (peso, aciertos menos errores, criterios de acierto en respuestas múltiples o numéricas) y se replican idénticas en el código y en el prompt.
- No se inventan normas: nada de CI, edad mental ni percentiles sin baremo propio validado. Las escalas por porcentaje se etiquetan como internas y provisionales.

## Tiempo

- Los tiempos límite se definen por serie y se documentan con su origen.
- Las modalidades de tiempo se asignan por tipo de puesto, nunca por candidato ni a criterio del aplicador en el momento.
- El límite realmente aplicado se guarda al iniciar cada serie y es el que se reporta.
- Cambiar un límite o un reactivo cambia la forma: versiona (`FORM_ID`) y no mezcles resultados de versiones distintas sin advertirlo.
