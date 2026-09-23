/* Razonamiento General, Forma B: lo propio de esta prueba. El motor común está en motor/motor.js;
   herramientas/construir.py une ambos con datos/ y marca/ en src/prueba.html. */
const TITULO = "Amador Russell, prueba de razonamiento general";
const TEST_NAME = "Prueba de Razonamiento General, Forma B";
/* Carpeta en GitHub Pages; debe coincidir con el nombre de la carpeta de la prueba. */
const CARPETA = "razonamiento-forma-b";
/* Base de las claves de localStorage: propia de cada prueba para que no compartan estado. */
const CLAVE_BASE = "rgFormaB";
/* Modalidades de tiempo, fijas por tipo de puesto (no por candidato) */
const MODES = {
  std:{label:"Estándar",  puesto:"Administrativo o técnico", factor:1},
  ext:{label:"Extendida", puesto:"Operativo: campo, empaque, taller o logística", factor:1.25}
};
/* Frase de la bienvenida del candidato, después de "Gracias por tu interés en Amador Russell." */
const BIENVENIDA = "Esta prueba mide cómo razonas, no lo que sabes de un oficio.";
/* Series en orden. enunciado: texto fijo arriba de las opciones cuando el reactivo no trae el suyo. */
const META = [
 {id:"I",   name:"Frases incompletas",           title:"Completa la frase",            factor:"Información",  type:"single", time:130, rule:"aciertos", weight:1,
  howto:"Lee la frase y toca la opción que la completa correctamente.",
  example:{stem:"El iniciador de la guerra de Independencia de México fue:", options:["Morelos","Zaragoza","Iturbide","Hidalgo"], key:3}},
 {id:"II",  name:"Razonamiento verbal",          title:"Elige la mejor respuesta",     factor:"Juicio",       type:"single", time:130, rule:"aciertos", weight:2,
  howto:"Lee la pregunta y toca la respuesta más correcta. Solo una es la mejor.",
  example:{stem:"Compramos relojes porque:", options:["nos gusta oírlos sonar","tienen manecillas","nos indican la hora"], key:2}},
 {id:"III", name:"Sinónimos y antónimos",        title:"¿Mismo significado o contrario?", factor:"Vocabulario", type:"pair", time:130, rule:"neto", weight:1,
  howto:"Mira las dos palabras. Toca «Significan lo mismo» o «Significan lo contrario».",
  example:{a:"tirar", b:"arrojar", key:1}},
 {id:"IV",  name:"Atributos siempre presentes",  title:"Lo que siempre tiene",         factor:"Síntesis",     type:"multi2", time:180, rule:"aciertos", weight:1,
  howto:"Toca las DOS opciones que esa cosa tiene siempre, sin excepción. Debes elegir exactamente dos.",
  example:{stem:"Una persona tiene siempre:", options:["Cuerpo","Gorra","Guantes","Boca","Dinero"], key:[0,3]}},
 {id:"V",   name:"Problemas numéricos",          title:"Problemas con números",        factor:"Concentración", type:"num", time:300, rule:"aciertos", weight:2,
  howto:"Resuelve el problema y escribe solo el número con el teclado de la pantalla. Puedes usar punto decimal.",
  example:{stem:"Si un refresco cuesta $15, ¿cuánto cuestan 3 refrescos?", unit:"pesos", key:45}},
 {id:"VI",  name:"Juicio (Sí / No)",             title:"¿Sí o no?",                    factor:"Análisis",     type:"yesno", time:130, rule:"neto", weight:1,
  howto:"Lee la frase. Toca «Sí» si es cierta o «No» si no lo es.",
  example:{stem:"El carbón se hace de la madera.", key:1}},
 {id:"VII", name:"Analogías",                    title:"Relaciones entre palabras",    factor:"Abstracción",  type:"single", time:130, rule:"aciertos", weight:1,
  howto:"Descubre cómo se relacionan las dos primeras palabras y elige la que se relaciona de la misma forma con la tercera.",
  example:{stem:"OÍDO es a OÍR como OJO es a:", options:["mesa","ver","mano","jugar"], key:1}},
 {id:"VIII",name:"Oraciones desordenadas",       title:"Frases revueltas",             factor:"Planeación",   type:"scramble", time:190, rule:"aciertos", weight:1,
  howto:"Las palabras están revueltas. Ordénalas en tu mente y decide si lo que dice la frase es verdadero o falso.",
  example:{words:["oír","son","los","para","oídos"], key:1, solved:"Los oídos son para oír."}},
 {id:"IX",  name:"Elemento que no corresponde",  title:"La que no pertenece",          factor:"Organización", type:"single", time:190, rule:"aciertos", weight:1,
  howto:"Cuatro palabras forman un grupo. Toca la que no pertenece a ese grupo.",
  enunciado:"¿Cuál no pertenece al grupo?",
  example:{options:["Bala","Cañón","Pistola","Espada","Lápiz"], key:4}},
 {id:"X",   name:"Series numéricas",             title:"Sigue la serie",               factor:"Atención",     type:"series", time:240, rule:"aciertos", weight:2,
  howto:"Descubre cómo avanza la serie y escribe los DOS números que siguen. Toca cada casilla para escribir en ella.",
  example:{terms:["5","10","15","20"], key:[25,30]}}
];

/* ====== Prompt de calificación ======
   El motor arma datos de la aplicación, tablas, indicadores de proceso y respuestas;
   estas son las secciones propias de la prueba, en el orden en que aparecen. */
function reglaTexto(m){return m.rule==="neto"?"aciertos − errores (mín. 0)":m.type==="multi2"?"1 punto si marca exactamente las 2 correctas":m.type==="series"?"2 puntos si ambos números son correctos":(m.weight===1?"1 punto por acierto":m.weight+" puntos por acierto");}
const PROMPT = {
  descripcion: "Prueba de razonamiento general de 10 series con la estructura del Terman-Merrill. La Forma B es una versión propia de la empresa y no tiene baremos normativos publicados. Tiene dos modalidades de tiempo fijas según el tipo de puesto: estándar (administrativo o técnico) y extendida, con 25 % más tiempo (operativo: campo, empaque, taller o logística). La columna Límite muestra el tiempo que realmente se aplicó a este candidato. Cada serie se asocia con un factor:",
  reglas: [
    "- Las omisiones valen 0 y no restan.",
    "- Series III y VI (dos opciones): puntaje = aciertos − errores, con mínimo 0, para corregir el efecto del azar.",
    "- Serie IV: el reactivo es acierto solo si el candidato marcó exactamente las dos opciones correctas; una sola opción marcada cuenta como error.",
    "- Series V y X: respuestas numéricas; acepta equivalentes exactos (3.5 = 3.50). En la serie X el reactivo es acierto solo si ambos números son correctos."
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
    "Es una escala interna y provisional. No conviertas a CI, edad mental ni percentiles, y no uses las tablas del Terman-Merrill original: no aplican a esta forma.",
    ""
  ],
  tareas: [
    "## Tareas",
    "1. Recalcula el puntaje de cada serie con la clave y las reglas. Si tu cálculo difiere de la precalificación, usa el tuyo y señala la diferencia.",
    "2. Calcula el puntaje total y el porcentaje global, y asigna el nivel con la escala provisional.",
    "3. Asigna nivel a cada factor e identifica los factores más fuertes y los más débiles.",
    "4. Detecta patrones con la precalificación y los indicadores de proceso: omisiones no vistas al final de una serie (falta de tiempo) frente a omisiones vistas y dejadas en blanco; series con tiempo agotado; errores sistemáticos del mismo tipo; señales de respuesta al azar o de poco esfuerzo (respuestas rápidas concentradas con errores, misma letra repetida); y si los cambios de respuesta mejoraron o empeoraron el resultado. Compara los tiempos solo entre reactivos de la misma serie de este candidato: no hay tiempos de referencia, y tardar más en reactivos más difíciles es esperable.",
    "5. Considera la escolaridad declarada y los años desde que dejó la escuela al interpretar las series que dependen de conocimiento escolar (I, III, IV, VII y IX) y distingue falta de conocimiento de falta de razonamiento.",
    "6. Considera las condiciones de la aplicación (uso de teléfono o tablet, incidencias anotadas) antes de atribuir a la capacidad del candidato un resultado bajo, lento o con muchas omisiones. Si una condición pudo afectar una serie, dilo y trata esa serie con cautela.",
    "7. Relaciona el perfil con las exigencias cognitivas probables del puesto al que aspira dentro de una operación agrícola (por ejemplo: seguir instrucciones y dosis, calcular cantidades, llevar registros, detectar anomalías en campo o equipo, coordinar cuadrillas). No supongas funciones que el nombre del puesto no indique; si el puesto no está registrado, omite este punto.",
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
