/* Razonamiento con Figuras, Forma A: lo propio de esta prueba. El motor común está en motor/motor.js;
   herramientas/construir.py une ambos con datos/ y marca/ en src/prueba.html.
   Los reactivos, sus ejemplos y sus descripciones salen de fuentes/generar_reactivos.py. */
const TITULO = "Amador Russell, prueba de razonamiento con figuras";
const TEST_NAME = "Prueba de Razonamiento con Figuras, Forma A";
/* Carpeta en GitHub Pages; debe coincidir con el nombre de la carpeta de la prueba. */
const CARPETA = "razonamiento-figuras";
/* Base de las claves de localStorage: propia de cada prueba para que no compartan estado. */
const CLAVE_BASE = "rfFormaA";
/* Modalidades de tiempo, fijas por tipo de puesto (no por candidato) */
const MODES = {
  std:{label:"Estándar",  puesto:"Administrativo o técnico", factor:1},
  ext:{label:"Extendida", puesto:"Operativo: campo, empaque, taller o logística", factor:1.25}
};
/* Frase de la bienvenida del candidato, después de "Gracias por tu interés en Amador Russell." */
const BIENVENIDA = "Esta prueba mide cómo razonas con figuras. No necesitas leer ni hacer cuentas.";
/* Series en orden. El ejemplo de cada serie está en datos/ejemplos.json. */
const META = [
 {id:"A", name:"Completar el dibujo",        title:"Completa el dibujo",          factor:"Percepción de patrones", type:"figura", time:250, rule:"aciertos", weight:1,
  howto:"Al dibujo le falta un pedazo. Toca la pieza que lo completa sin que se note el corte."},
 {id:"B", name:"Analogías de 2 x 2",         title:"Lo que cambia",               factor:"Analogía",               type:"figura", time:310, rule:"aciertos", weight:1,
  howto:"Mira qué cambia de izquierda a derecha y de arriba abajo. Toca la figura que va en la casilla vacía."},
 {id:"C", name:"Progresiones de 3 x 3",      title:"Lo que va aumentando",        factor:"Progresión",             type:"figura", time:490, rule:"aciertos", weight:1,
  howto:"En cada fila algo aumenta, crece o gira paso a paso. Descubre cómo avanza y toca la figura que falta."},
 {id:"D", name:"Distribución de tres",       title:"Uno de cada uno",             factor:"Distribución",           type:"figura", time:550, rule:"aciertos", weight:1,
  howto:"En cada fila y en cada columna hay una figura de cada tipo. Toca la que falta para completar la fila."},
 {id:"E", name:"Combinación de trazos",      title:"Juntar y quitar",             factor:"Combinación de figuras", type:"figura", time:610, rule:"aciertos", weight:1,
  howto:"La tercera casilla de cada fila sale de juntar o quitar líneas de las dos primeras. Descubre cómo y toca la que falta."}
];

/* ====== Prompt de calificación ======
   El motor arma datos de la aplicación, tablas, indicadores de proceso y respuestas;
   estas son las secciones propias de la prueba, en el orden en que aparecen. */
function reglaTexto(m){return "1 punto por acierto";}
const PROMPT = {
  descripcion: "Prueba no verbal de razonamiento con figuras de 5 series de 12 reactivos, del tipo de las matrices progresivas: el candidato elige la figura que completa un dibujo o una matriz. Es una forma propia de la empresa, con figuras y reglas diseñadas para ella; no es una prueba publicada ni tiene baremos normativos. Las series van de menor a mayor dificultad y cada una exige un tipo de regla distinto. Las series A y B tienen 6 opciones por reactivo (azar: 1 de 6); C, D y E tienen 8 (azar: 1 de 8). Tiene dos modalidades de tiempo fijas según el tipo de puesto: estándar (administrativo o técnico) y extendida, con 25 % más tiempo (operativo: campo, empaque, taller o logística). La columna Límite muestra el tiempo que realmente se aplicó a este candidato. Cada serie se asocia con un factor:",
  reglas: [
    "- 1 punto por acierto en todas las series; las omisiones y los errores valen 0 y no restan.",
    "- No se corrige por azar. Con 60 reactivos, contestar todo al azar da en promedio unos 8.5 aciertos (2 por serie en A y B, 1.5 por serie en C, D y E); un puntaje cercano a ese valor no demuestra razonamiento.",
    "- Cada reactivo tiene una sola respuesta correcta: la regla que la determina aparece junto al reactivo en la sección de respuestas."
  ],
  escala: [
    "## Escala interpretativa provisional",
    "Porcentaje del puntaje máximo, aplicable al total y a cada serie:",
    "- 90 a 100: Superior",
    "- 75 a 89: Superior al promedio",
    "- 50 a 74: Promedio",
    "- 25 a 49: Inferior al promedio",
    "- 0 a 24: Deficiente",
    "",
    "Es una escala interna y provisional. No conviertas a CI, percentiles ni rangos de ninguna prueba publicada de matrices (por ejemplo, las Matrices Progresivas de Raven): sus baremos no aplican a esta forma.",
    ""
  ],
  tareas: [
    "## Tareas",
    "1. Recalcula el puntaje de cada serie con la clave. Si tu cálculo difiere de la precalificación, usa el tuyo y señala la diferencia.",
    "2. Calcula el puntaje total y el porcentaje global, y asigna el nivel con la escala provisional.",
    "3. Asigna nivel a cada factor e identifica los más fuertes y los más débiles. Considera que la dificultad crece dentro de cada serie y de una serie a la siguiente: es esperable fallar más al final de cada serie y en D y E.",
    "4. Detecta patrones con la precalificación y los indicadores de proceso: omisiones no vistas al final de una serie (falta de tiempo) frente a omisiones vistas y dejadas en blanco; series con tiempo agotado; aciertos en reactivos difíciles con errores en fáciles de la misma serie (inconsistencia que sugiere azar o distracción); errores que eligen siempre el mismo tipo de figura equivocada según su descripción (por ejemplo, copiar una casilla vecina o acertar un atributo y fallar otro); señales de respuesta al azar o de poco esfuerzo (respuestas rápidas concentradas con errores, misma posición repetida); y si los cambios de respuesta mejoraron o empeoraron el resultado. Compara los tiempos solo entre reactivos de la misma serie de este candidato: no hay tiempos de referencia.",
    "5. La prueba casi no depende de la lectura ni del conocimiento escolar, pero sí de la costumbre de resolver ejercicios de este tipo y de usar pantallas táctiles. Considera la escolaridad, los años desde que dejó la escuela y el uso de teléfono o tablet al interpretar un resultado bajo, sin usarlos para ajustar el puntaje.",
    "6. Considera las condiciones de la aplicación (uso de teléfono o tablet, incidencias anotadas) antes de atribuir a la capacidad del candidato un resultado bajo, lento o con muchas omisiones. Si una condición pudo afectar una serie, dilo y trata esa serie con cautela.",
    "7. Relaciona el perfil con las exigencias cognitivas probables del puesto al que aspira dentro de una operación agrícola (por ejemplo: aprender procedimientos nuevos, detectar anomalías en campo o equipo, seguir una secuencia de pasos, resolver problemas sin instrucciones escritas). No supongas funciones que el nombre del puesto no indique; si el puesto no está registrado, omite este punto.",
    "8. Emite una conclusión: Recomendable, Recomendable con reservas o No recomendable, con su justificación.",
    ""
  ],
  formato: [
    "## Formato de salida",
    "Responde en español con estas secciones, en este orden:",
    "1. Resumen: una línea con puntaje total, porcentaje, nivel y conclusión.",
    "2. Tabla de calificación por serie: serie, factor, aciertos, errores, omisiones, puntaje, máximo, porcentaje y nivel.",
    "3. Perfil de factores: fortalezas y áreas débiles, con evidencia (reactivos concretos).",
    "4. Patrones de respuesta, uso del tiempo y condiciones de la aplicación.",
    "5. Ajuste al puesto.",
    "6. Conclusión y recomendaciones para la entrevista (qué explorar o verificar).",
    "7. Limitaciones de la interpretación.",
    ""
  ],
  restricciones: [
    "## Restricciones",
    "- No inventes datos que no estén en este mensaje.",
    "- Distingue hechos (datos de la prueba) de inferencias.",
    "- Indica en una línea que esta prueba no basta por sí sola para decidir una contratación.",
    "- Usa lenguaje respetuoso y sin etiquetas diagnósticas.",
    "- No uses la edad para ajustar el puntaje, inferir capacidades ni fundamentar la conclusión: no hay baremo por edad y la ley prohíbe discriminar por edad al contratar. Si un resultado parece afectado por las condiciones de la aplicación, fundaméntalo en esas condiciones, no en la edad.",
    "- Compara este resultado solo con candidatos evaluados en la misma modalidad de tiempo. No ajustes ni corrijas el puntaje por la modalidad."
  ]
};
