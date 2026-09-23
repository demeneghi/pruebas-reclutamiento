# Decisiones del proyecto

## Formato y diseño

- Un solo HTML autocontenido para que funcione sin conexión en ranchos. Las fuentes (Atkinson Hyperlegible 400 y 700, subconjunto latino) van incrustadas en base64: distingue bien 0/O y 1/l, útil en series numéricas.
- Metáfora de hoja de respuestas: fondo de cuadrícula tenue, opciones con burbuja que se rellena al elegir, acento amarillo lápiz. Solo modo claro, forzado con `color-scheme: light only`.
- Una pregunta por pantalla, botones de al menos 56 px de alto, tipografía de 18 a 20 px.
- Marca: encabezado de texto "Amador Russell, Reclutamiento y selección" en aplicador, final y resultados. En la bienvenida, el logotipo animado ocupa el lugar del nombre.
- Logotipo: vectorizado desde `marca/logo-amador-russell.png` con `marca/vectorizar_logo.py` e incrustado en la constante `LOGO` (unos 11 KB). Sus colores (verde `#155750`, amarillo `#F9D408`) solo se usan en el logotipo; la paleta de la aplicación no cambia.
- Animación del logotipo: unos 2.4 s, una sola vez al abrir la bienvenida y otra si se toca el logotipo. Solo usa transformaciones, opacidad y recortes; con "reducir movimiento" activado en el dispositivo se muestra fijo. No aparece durante las partes con tiempo.

## Flujo

1. Pantalla del aplicador: nombre, edad, escolaridad, años desde que dejó la escuela (opcional), uso de teléfono o tablet (opcional), puesto, tipo de puesto (obligatorio), rancho o área (opcional), aplicador, con o sin tiempo límite.
2. Bienvenida del candidato: logotipo animado, saludo y cuatro reglas (partes, ejemplo, tiempo, no regresar).
3. Por cada serie: introducción con ejemplo interactivo que no cuenta, preguntas, revisión con cuadrícula y cierre. Una serie cerrada no se puede reabrir.
   - Pantalla completa: se pide sola al tocar "Comenzar". Si el candidato sale de ella, la introducción de cada serie muestra el botón "Pantalla completa" para volver; no aparece durante las preguntas para no distraer con el reloj corriendo. Donde el navegador no la permite (Safari de iPhone, o una página incrustada que la bloquee) el botón no se muestra.
4. Pantalla final. Los resultados se abren manteniendo presionado un botón 1.5 s.
5. Resultados: tabla resumen, campo de incidencias del aplicador y prompt (copiar, compartir, descargar .txt). Las incidencias actualizan el prompt al escribirlas y se guardan con la aplicación, también al editarlas desde el historial.

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

## Registro por reactivo

- Por cada reactivo se guarda en `S.log`: tiempo acumulado en pantalla, tiempo en pantalla hasta la primera respuesta, primera respuesta, última respuesta registrada y número de cambios.
- Solo cuenta el tiempo con el reactivo visible: no suman la revisión, otras pantallas ni la pantalla apagada. El tiempo acumulado se consolida en cada guardado, así que una recarga conserva lo transcurrido.
- La respuesta se registra al elegir, al completar las dos opciones de la serie IV, con "Listo" en V y X, o al salir del reactivo si quedó contestada. Escribir cifras no cuenta como respuesta hasta ese momento.
- Respuesta rápida: primera respuesta en menos de 2 s (`RAPIDA_MS`). Umbral interno y provisional, pendiente de calibrar con la aplicación piloto. No hay tiempos de referencia: el prompt pide comparar tiempos solo dentro de la misma serie del candidato.
- Omisión vista: el reactivo apareció en pantalla y quedó en blanco. Omisión no vista: el candidato nunca llegó a él. Distingue falta de tiempo de reactivos saltados.
- El registro no cambia reactivos ni límites, así que no cambia `FORM_ID`. Una aplicación iniciada antes del registro se reanuda sin él y el prompt advierte que no hay tiempos por reactivo.

## Condiciones de la aplicación y edad

- Los años desde que dejó la escuela y el uso de teléfono o tablet explican un resultado bajo o lento mejor que la edad, y se capturan en su lugar como contexto.
- La edad aparece en el prompt solo para identificar al candidato. El prompt prohíbe usarla para ajustar el puntaje, inferir capacidades o fundamentar la conclusión: no hay baremo por edad y la Ley Federal del Trabajo (art. 133) y la Ley Federal para Prevenir y Eliminar la Discriminación prohíben negar empleo por edad.

## Persistencia

- localStorage con clave `rgFormaB.v1`, copia idéntica en `rgFormaB.v1.respaldo` y verificación por relectura en cada guardado.
- Al recargar, la prueba en curso se reanuda sola en la misma pregunta. Si la versión de los reactivos cambió (`FORM_ID`), se archiva y el aplicador decide.
- Si la prueba se abre en otra pestaña, la anterior se bloquea.
- Historial de las últimas 30 aplicaciones en `rgFormaB.v1.historial`.
- Menú oculto del aplicador: mantener presionado 3 s el título de la bienvenida, de la parte o de la pantalla de tiempo terminado. Ofrece cancelar la aplicación y, servida desde Pages, cancelar y volver al menú de pruebas. En ambos casos la aplicación se archiva como cancelada antes de limpiar el estado.
- Banner rojo fijo si falla el guardado; aviso si el navegador no permite guardar o si es un navegador embebido de otra app.

## Prompt de calificación

Incluye rol, contexto de la empresa, datos y condiciones de la aplicación con las incidencias, modalidad y límite real por serie, reglas, escala provisional, precalificación automática, indicadores de proceso por serie, respuestas reactivo por reactivo con clave, tiempo de primera respuesta y cambios, tareas, formato de salida y restricciones. Prohíbe convertir a CI, comparar entre modalidades y usar la edad en la interpretación.

## Publicación

- GitHub Pages: https://demeneghi.github.io/pruebas-reclutamiento/razonamiento-forma-b/. El workflow `.github/workflows/pages.yml` publica solo `src/prueba.html`; `datos/`, `fuentes/` y `docs/` no llegan al sitio. La página lleva `noindex` para que los buscadores no la listen.
- El sitio de Pages es público aunque el repositorio sea privado. La clave viaja ofuscada en base64 dentro del HTML, aceptable solo para aplicación presencial con el dispositivo en manos del aplicador.
- Todas las páginas de Pages de la cuenta comparten el origen `demeneghi.github.io` y, por tanto, el localStorage: no publicar en esa cuenta páginas de terceros ni código que lea el almacenamiento. Única excepción: el menú de la raíz (`sitio/index.html`) lee `rgFormaB.v1` y su respaldo para reabrir una aplicación en curso. Con "Preparar para un candidato nuevo" (pulsación larga de 3 s y confirmación) archiva en `rgFormaB.v1.historial` la aplicación pendiente, cancelada si no estaba terminada y con el reloj de la parte abierta cerrado en su hora límite si ya venció. Solo después de verificar el archivo borra el estado. El historial no se borra; la confirmación muestra el nombre del candidato.
- La pantalla del aplicador ofrece "Cambiar de prueba" (enlace a `../`) solo cuando la ruta termina en `/razonamiento-forma-b/` (constante `CARPETA`); en el artefacto o como archivo local no aparece.
- Artefacto privado de Claude. Las descargas usan la capacidad `claude.use("downloads")` y, fuera de Claude, un enlace de descarga normal.
- El historial depende del dominio: un dispositivo que aplicó desde el artefacto no ve ese historial en Pages, y viceversa. Cada dispositivo usa un solo enlace.
- Alternativas evaluadas: Netlify Drop, Cloudflare Pages y Vercel Drop.
