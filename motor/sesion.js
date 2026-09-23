/* ====== Sesión del candidato ======
   La comparten el menú de pruebas (sitio/index.html) y cada prueba servida desde GitHub Pages:
   datos del candidato capturados una vez en el menú y resultado de cada prueba aplicada, con su prompt.
   Se guarda como el estado de las pruebas: al instante, verificado por relectura y con copia de respaldo.
   herramientas/construir.py la copia en ambos lados; se edita solo aquí. */
const SESION = "arSesion.v1", SESION_BAK = SESION+".respaldo", SESION_ARCH = SESION+".historial";
function sesionValida(o){return !!o&&typeof o==="object"&&typeof o.id==="string"&&!!o.cand&&typeof o.cand==="object"&&typeof o.cand.nombre==="string"&&!!o.pruebas&&typeof o.pruebas==="object";}
function sesionLeer(){
  for(const k of [SESION,SESION_BAK]){try{const o=JSON.parse(localStorage.getItem(k));if(sesionValida(o))return o;}catch(e){}}
  return null;
}
function sesionGuardar(s){
  s.rev=(s.rev||0)+1;s.guardada=Date.now();
  const t=JSON.stringify(s);
  try{
    localStorage.setItem(SESION,t);
    if(localStorage.getItem(SESION)!==t) return false;
    localStorage.setItem(SESION_BAK,t);
    return true;
  }catch(e){return false;}
}
function sesionBorrar(){try{localStorage.removeItem(SESION);localStorage.removeItem(SESION_BAK);}catch(e){}}
function sesionHistorial(){try{const a=JSON.parse(localStorage.getItem(SESION_ARCH)||"[]");return Array.isArray(a)?a.filter(sesionValida):[];}catch(e){return [];}}
/* Archiva la sesión (últimas 30) y confirma que quedó guardada. */
function sesionArchivar(s){
  const a=sesionHistorial(), i=a.findIndex(x=>x.id===s.id);
  if(i>=0)a[i]=s;else a.unshift(s);
  while(a.length>30)a.pop();
  for(;;){try{localStorage.setItem(SESION_ARCH,JSON.stringify(a));break;}catch(e){if(a.length<=1)return false;a.pop();}}
  return sesionHistorial().some(x=>x.id===s.id);
}
/* Línea de incidencias del prompt. La prueba la escribe al terminar y el menú la reemplaza con lo que anote el aplicador. */
const INCID_PREFIJO = "- Incidencias anotadas por el aplicador: ";
function lineaIncidencias(t){t=(t||"").trim();return INCID_PREFIJO+(t?"«"+t.replace(/\s+/g," ")+"»":"ninguna");}
