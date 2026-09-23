/* ====== Motor común de las pruebas ======
   herramientas/construir.py lo coloca después de la configuración de cada prueba (src/config.js),
   que define TEST_NAME, CARPETA, CLAVE_BASE, MODES, BIENVENIDA, META, reglaTexto y PROMPT,
   y de los datos incrustados LOGO (marca/), ITEMS y KEY (datos/), más EJEMPLOS y DESC si la prueba los trae.
   Nada de aquí es propio de una prueba. */
const COMPANY = "Amador Russell";
const COMPANY_LEGAL = "Amador Russell SPR de RL";
const COMPANY_DESC = "empresa agrícola productora de piña MD2 en Veracruz, México";
/* Solo servida desde su carpeta de GitHub Pages se ofrece volver al menú de pruebas de la raíz. */
const MENU = new RegExp("/"+CARPETA+"/(index\\.html)?$").test(location.pathname);
function timeFor(m,mode){const f=(MODES[mode||S.mode]||MODES.std).factor;return Math.round(m.time*f/10)*10;}
function totalFor(mode){return META.reduce((a,m)=>a+timeFor(m,mode),0);}
const brand = () => '<div class="brand"><b>'+COMPANY+'</b><span>Reclutamiento y selección</span></div>';
const brandLogo = () => '<div class="brand hero">'+LOGO+'<span>Reclutamiento y selección</span></div>';
const LETTERS = "ABCDE";
/* Ejemplo de práctica de la serie: en config.js (m.example) o, si no cabe ahí, en datos/ejemplos.json. */
function ejemplo(m){return m.example||(typeof EJEMPLOS!=="undefined"&&EJEMPLOS[m.id])||null;}
/* Regla y opciones en texto de un reactivo (datos/descripciones.json), para el prompt. */
function desc(m,i){return typeof DESC!=="undefined"&&DESC[m.id]?DESC[m.id][i]:null;}

/* ====== Persistencia ======
   - Cada cambio se guarda al instante en localStorage y se verifica leyéndolo de vuelta.
   - Se escribe una segunda copia idéntica como respaldo por si la principal se daña.
   - Al recargar, la prueba en curso se reanuda sola en el punto exacto; el reloj sigue corriendo
     con la hora límite guardada, así que recargar no da tiempo extra.
   - Si la prueba se abre en otra pestaña, la pestaña vieja se bloquea para no pisar respuestas.
   - Cada aplicación terminada o cancelada se archiva en un historial del dispositivo (últimas 30). */
const STORE = CLAVE_BASE+".v1", STORE_BAK = STORE+".respaldo", ARCH = STORE+".historial";
const PHASES = ["setup","welcome","intro","item","review","timeout","done","results"];
const TAB = now36()+Math.random().toString(36).slice(2,8);
function now36(){return Date.now().toString(36);}
function hashStr(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0).toString(36);}
const FORM_ID = hashStr(JSON.stringify(ITEMS));
const STORAGE_OK = (()=>{try{const k=CLAVE_BASE+".prueba";localStorage.setItem(k,"1");const ok=localStorage.getItem(k)==="1";localStorage.removeItem(k);return ok;}catch(e){return false;}})();
let SAVE_FAIL=false, BLOCKED=false;
function valid(o){return !!o&&typeof o==="object"&&PHASES.includes(o.phase)&&o.ans&&typeof o.ans==="object"&&o.times&&typeof o.times==="object"&&Number.isInteger(o.si)&&o.si>=0&&o.si<META.length&&Number.isInteger(o.ii)&&o.ii>=0;}
function parseState(txt){try{const o=JSON.parse(txt);return valid(o)?o:null;}catch(e){return null;}}
function cleanJSON(o){return JSON.stringify(o,(k,v)=>k.charAt(0)==="_"?undefined:v);}
function load(){
  if(!STORAGE_OK) return null;
  try{return parseState(localStorage.getItem(STORE))||parseState(localStorage.getItem(STORE_BAK));}catch(e){return null;}
}
function save(){
  if(!S||S._archived||BLOCKED||!STORAGE_OK||S.phase==="setup") return;
  checkpoint();
  S.form=FORM_ID;S.tab=TAB;S.rev=(S.rev||0)+1;S.savedAt=Date.now();
  const data=cleanJSON(S);
  try{
    localStorage.setItem(STORE,data);
    if(localStorage.getItem(STORE)!==data) throw new Error("verificación");
    localStorage.setItem(STORE_BAK,data);
    if(SAVE_FAIL){SAVE_FAIL=false;saveBanner();}
  }catch(e){SAVE_FAIL=true;saveBanner();}
}
function clearStore(){try{localStorage.removeItem(STORE);localStorage.removeItem(STORE_BAK);}catch(e){}}
function archiveLoad(){if(!STORAGE_OK)return [];try{const a=JSON.parse(localStorage.getItem(ARCH)||"[]");return Array.isArray(a)?a.filter(valid):[];}catch(e){return [];}}
function archivePut(st){
  if(!STORAGE_OK||!st||!st.id) return;
  const a=archiveLoad(), c=JSON.parse(cleanJSON(st)), i=a.findIndex(x=>x.id===c.id);
  if(i>=0)a[i]=c;else a.unshift(c);
  while(a.length>30)a.pop();
  for(;;){try{localStorage.setItem(ARCH,JSON.stringify(a));return;}catch(e){if(a.length<=1)return;a.pop();}}
}
function saveBanner(){
  let b=document.getElementById("savewarn");
  if(!SAVE_FAIL){if(b)b.remove();return;}
  if(!b){b=document.createElement("div");b.id="savewarn";b.className="savewarn";b.setAttribute("role","alert");document.body.appendChild(b);}
  b.textContent="No se pudo guardar el avance en este dispositivo. No recargues ni cierres la página y avisa a quien aplica la prueba.";
}
function showBlocked(){
  const w=document.createElement("div");w.className="scrim";w.style.zIndex="60";
  w.innerHTML='<div class="modal" role="alertdialog"><h2>Esta ventana se bloqueó</h2><p>La prueba se abrió en otra pestaña o ventana. Para no dañar las respuestas, sigue solo en la otra y cierra esta.</p></div>';
  document.body.appendChild(w);
}

/* ====== Estado ====== */
let EX = null;          // estado del ejemplo (no se guarda)
let SLOT = 0;           // casilla activa en teclado numérico
let advanceTok = 0;

/* Registro por reactivo para los indicadores de proceso del prompt.
   S.log[serie][i] = {d, f, a, u, c}
   d: ms acumulados con el reactivo en pantalla (no cuenta otras pantallas ni la pantalla apagada)
   f: ms en pantalla hasta la primera respuesta; null si nunca respondió
   a: primera respuesta; u: última respuesta registrada (JSON); c: veces que cambió la respuesta
   La respuesta se registra al elegir, al completar las dos opciones (IV), con "Listo" (V y X)
   o al salir del reactivo si quedó contestada. */
let VIEW = null;
function logRec(id,i){if(!S.log)S.log={};if(!S.log[id])S.log[id]=ITEMS[id].map(()=>null);return S.log[id][i]||(S.log[id][i]={d:0,f:null,a:null,u:null,c:0});}
/* Si el reloj del dispositivo retrocede (ajuste de hora, o el reloj simulado de las pruebas), el tramo cuenta 0, nunca negativo. */
function checkpoint(){if(VIEW&&VIEW.t!=null){const n=Date.now();logRec(VIEW.id,VIEW.i).d+=Math.max(0,n-VIEW.t);VIEW.t=n;}}
function commitAns(id,i){
  const m=META.find(x=>x.id===id), v=ansArr(id)[i];
  if(!isAnswered(m,v)) return;
  checkpoint();
  const r=logRec(id,i), s=JSON.stringify(v);
  if(r.f==null){r.f=r.d;r.a=JSON.parse(s);}
  else if(s!==r.u) r.c++;
  r.u=s;
}
function leaveView(){if(!VIEW)return;checkpoint();commitAns(VIEW.id,VIEW.i);VIEW=null;}
function track(){
  const k=S.phase==="item"&&!S._archived&&!BLOCKED?meta().id+":"+S.ii:null;
  if(VIEW&&VIEW.k===k) return;
  leaveView();
  if(k){VIEW={k,id:meta().id,i:S.ii,t:document.visibilityState==="hidden"?null:Date.now()};logRec(VIEW.id,VIEW.i);}
}
function blank(){return {id:"A"+now36()+Math.random().toString(36).slice(2,6),status:"en curso",phase:"setup",cand:{},timed:true,mode:null,si:0,ii:0,ans:{},times:{},startedAt:null,finishedAt:null};}
let S = blank();
let RESUMED = false;
(function boot(){
  const saved=load();
  if(!saved||saved.phase==="setup") return;
  if(!saved.id) saved.id="A"+now36();
  if(saved.form&&saved.form!==FORM_ID){archivePut(saved);S._resume=saved;return;}
  S=saved; RESUMED=true;
  if(S.phase==="results") S.phase="done";
  if(S.phase==="done") archivePut(S);
})();
if(RESUMED) save();
/* ====== Sesión del menú ======
   Servida desde Pages, la prueba toma al candidato de la sesión que capturó el menú y empieza en la bienvenida.
   Sin sesión, o si esta prueba ya se aplicó en la sesión, regresa al menú. Abierta como archivo o artefacto
   (sin menú) o sin almacenamiento, conserva su pantalla de captura propia. */
const SES = MENU&&STORAGE_OK ? sesionLeer() : null;
let AL_MENU = false;
(function conSesion(){
  if(!MENU||!STORAGE_OK||S._resume) return;
  /* Una aplicación terminada de otra sesión ya está en el historial: se limpia para el candidato actual. */
  if(RESUMED&&S.phase==="done"&&(!SES||S.sesion!==SES.id)){clearStore();S=blank();RESUMED=false;}
  if(RESUMED) return;
  const previa=SES&&SES.pruebas[CARPETA];
  if(!SES||(previa&&previa.estado==="terminada")){AL_MENU=true;return;}
  S.cand=Object.assign({},SES.cand);S.mode=SES.mode;S.timed=SES.timed!==false;S.sesion=SES.id;S.phase="welcome";save();
})();
if(AL_MENU) location.replace("../");

/* ====== Utilidades ====== */
const $ = s => document.querySelector(s);
const esc = s => String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const now = () => Date.now();
function fmt(ms){ms=Math.max(0,Math.round(ms/1000));return Math.floor(ms/60)+":"+String(ms%60).padStart(2,"0");}
function toast(t){const e=$("#toast");e.textContent=t;e.classList.add("show");clearTimeout(e._t);e._t=setTimeout(()=>e.classList.remove("show"),1800);}
function fmtT(s){const mi=Math.floor(s/60),se=s%60;return mi+" min"+(se?" "+se+" s":"");}
function meta(){return META[S.si];}
function items(){return ITEMS[meta().id];}
function ansArr(id){if(!S.ans[id])S.ans[id]=ITEMS[id].map(()=>null);return S.ans[id];}
function isAnswered(m,v){
  if(v==null) return false;
  if(m.type==="multi2") return v.length>0;
  if(m.type==="num") return v!=="";
  if(m.type==="series") return (v[0]||"")!==""||(v[1]||"")!=="";
  return true;
}
function numEq(s,k){if(s==null)return false;const t=String(s).replace(",",".");if(t===""||t===".")return false;const x=parseFloat(t);return isFinite(x)&&Math.abs(x-k)<1e-9;}
function correct(m,v,k){
  if(!isAnswered(m,v)) return null;
  switch(m.type){
    case "multi2": return v.length===2 && [...v].sort().join()===[...k].sort().join();
    case "num": return numEq(v,k);
    case "series": return numEq(v[0],k[0]) && numEq(v[1],k[1]);
    default: return v===k;
  }
}

/* ====== Modal ====== */
function modal(title,text,btns){
  const w=document.createElement("div");w.className="scrim";
  w.innerHTML='<div class="modal" role="dialog" aria-modal="true"><h2>'+esc(title)+'</h2><p>'+esc(text)+'</p><div class="row"></div></div>';
  const row=w.querySelector(".row");
  btns.forEach(b=>{const x=document.createElement("button");x.className="btn "+(b.cls||"");x.textContent=b.label;x.onclick=()=>{w.remove();b.fn&&b.fn();};row.appendChild(x);});
  document.body.appendChild(w);row.lastChild.focus();
}

/* ====== Render principal ====== */
function render(){
  const app=$("#app");
  const f={setup,welcome,intro,item,review,timeout,done,results}[S.phase];
  track();
  app.innerHTML=f();
  window.scrollTo(0,0);
  tick();
}

/* ---- Aplicador: datos ---- */
function setup(){
  const r=S._resume, c=S.cand||{};
  const resume = r ? '<div class="notice"><p><b>Hay una prueba sin terminar</b> de '+esc(r.cand.nombre||"sin nombre")+' (parte '+(r.si+1)+' de '+META.length+'), iniciada con otra versión de este archivo. Ya quedó copiada en el historial.</p><div class="row"><button class="btn" data-act="resume">Continuar esa prueba</button><button class="btn ghost" data-act="discard">Descartarla</button></div></div>' : "";
  const ua=navigator.userAgent||"";
  const inApp=/; wv\)|Telegram|FBAN|FBAV|Instagram|WhatsApp|Line\//i.test(ua);
  const warnApp = inApp ? '<div class="notice bad"><p><b>Estás dentro del navegador de otra aplicación.</b> Puede borrar el avance al cerrarse. Para aplicar la prueba ábrela en Chrome o Safari.</p></div>' : "";
  const warn = warnApp + (STORAGE_OK ? "" : '<div class="notice bad"><p><b>Este navegador no permite guardar el avance.</b> Si la página se recarga o se cierra, la prueba se pierde. Abre el archivo en Chrome o usa el enlace publicado.</p></div>');
  const hist = archiveLoad();
  const histHTML = hist.length ? '<h2>Resultados guardados en este dispositivo</h2><div class="hist">'+hist.map(h=>'<button data-act="openArch" data-v="'+esc(h.id)+'"><b>'+esc(h.cand&&h.cand.nombre||"Sin nombre")+'</b><span>'+new Date(h.startedAt||h.savedAt||0).toLocaleDateString("es-MX",{day:"numeric",month:"short",year:"numeric"})+', '+esc(h.status||"")+'</span></button>').join("")+'</div><button class="btn quiet" data-act="clearArch">Borrar historial</button>' : "";
  return '<div class="sheet">'+brand()+'<div class="toprow"><p class="muted small">Pantalla para quien aplica la prueba</p>'+(MENU?'<a class="btn quiet" href="../">Cambiar de prueba</a>':'')+'</div><h1>'+esc(TEST_NAME)+'</h1>'+warn+resume+
  '<p class="muted">Llena los datos del candidato y entrega el dispositivo. Con tiempo límite, la prueba dura unos '+Math.round(totalFor("std")/60)+' minutos en modalidad estándar y '+Math.round(totalFor("ext")/60)+' en extendida.</p>'+
  '<label class="f"><span>Nombre completo del candidato</span><input id="f-nombre" autocomplete="off" value="'+esc(c.nombre)+'"></label>'+
  '<div class="row"><label class="f" style="flex:1 1 120px"><span>Edad</span><input id="f-edad" inputmode="numeric" maxlength="2" value="'+esc(c.edad)+'"></label>'+
  '<label class="f" style="flex:3 1 220px"><span>Escolaridad terminada</span><select id="f-esc">'+["","Sin estudios","Primaria","Secundaria","Preparatoria o bachillerato","Carrera técnica","Licenciatura","Posgrado"].map(x=>'<option'+(x===c.esc?" selected":"")+'>'+x+'</option>').join("")+'</select></label></div>'+
  '<div class="row"><label class="f" style="flex:1 1 120px"><span>Años desde que dejó la escuela <small class="muted">(opcional)</small></span><input id="f-anos" inputmode="numeric" maxlength="2" value="'+esc(c.anos)+'"></label>'+
  '<label class="f" style="flex:3 1 220px"><span>Uso de teléfono o tablet <small class="muted">(opcional)</small></span><select id="f-disp">'+["","A diario","De vez en cuando","Casi nunca"].map(x=>'<option'+(x===c.disp?" selected":"")+'>'+x+'</option>').join("")+'</select></label></div>'+
  '<label class="f"><span>Puesto al que aspira</span><input id="f-puesto" autocomplete="off" value="'+esc(c.puesto)+'"></label>'+
  '<p style="font-weight:700;margin-bottom:6px;font-size:.92em">Tipo de puesto</p>'+
  '<div class="seg">'+["std","ext"].map(k=>'<button data-act="mode" data-v="'+k+'" aria-pressed="'+(S.mode===k)+'"><b>'+MODES[k].puesto+'</b><small>'+(k==="ext"?"Tiempo extendido, "+Math.round((MODES.ext.factor-1)*100)+" % más":"Tiempo estándar")+'</small></button>').join("")+'</div>'+
  '<label class="f"><span>Rancho o área <small class="muted">(opcional)</small></span><input id="f-sede" autocomplete="off" value="'+esc(c.sede)+'"></label>'+
  '<label class="f"><span>Nombre de quien aplica</span><input id="f-aplic" autocomplete="off" value="'+esc(c.aplic)+'"></label>'+
  '<p style="font-weight:700;margin-bottom:6px;font-size:.92em">Tiempo por parte</p>'+
  '<div class="seg"><button data-act="timed" data-v="1" aria-pressed="'+(S.timed?"true":"false")+'"><b>Con tiempo límite</b><small>Según el tipo de puesto</small></button><button data-act="timed" data-v="0" aria-pressed="'+(!S.timed?"true":"false")+'"><b>Sin límite (piloto)</b><small>Solo se registra el tiempo</small></button></div>'+
  '<button class="btn block" data-act="toWelcome">Entregar al candidato</button>'+histHTML+'</div>';
}
function readSetup(){
  S.cand={nombre:$("#f-nombre").value.trim(),edad:$("#f-edad").value.trim(),esc:$("#f-esc").value,anos:$("#f-anos").value.trim(),disp:$("#f-disp").value,puesto:$("#f-puesto").value.trim(),sede:$("#f-sede").value.trim(),aplic:$("#f-aplic").value.trim()};
}

/* ---- Botón visible para salir de la prueba ----
   Un toque corto solo avisa; mantenerlo 3 s abre el menú del aplicador (como el título de la parte). */
const salirBtn = () => '<button class="salir" data-hold="menu" aria-label="Salir de la prueba. Solo quien aplica: mantener presionado 3 segundos"><i></i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4"/><path d="M9 16l-4-4 4-4"/><path d="M5 12h10"/></svg><span>Salir</span></button>';
const salirFila = () => '<div class="salir-fila">'+salirBtn()+'</div>';

/* ---- Bienvenida candidato ---- */
const ICO={
  partes:'<circle cx="5" cy="6" r="1.8"/><circle cx="5" cy="12" r="1.8"/><circle cx="5" cy="18" r="1.8"/><path d="M10 6h10M10 12h10M10 18h10"/>',
  ejemplo:'<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
  tiempo:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  cierre:'<rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5v-3a4 4 0 0 1 8 0v3"/>'
};
function rule(k,t,s){
  return '<li><span class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+ICO[k]+'</svg></span><div><b>'+t+'</b><small>'+s+'</small></div></li>';
}
function welcome(){
  const first=(S.cand.nombre||"").split(/\s+/)[0];
  const total=totalFor();
  return '<div class="sheet">'+brandLogo()+'<h1 data-hold="menu">Hola'+(first?", "+esc(first):"")+'</h1>'+
  '<p class="lead">Gracias por tu interés en '+COMPANY+'. '+BIENVENIDA+'</p>'+
  '<ul class="rules">'+
  rule("partes",META.length+" partes cortas","Todo se contesta tocando la pantalla.")+
  rule("ejemplo","Primero, un ejemplo","Cada parte empieza con uno para practicar. No cuenta.")+
  (S.timed?rule("tiempo","Unos "+Math.round(total/60)+" minutos en total","Cada parte tiene su tiempo; lo verás arriba a la derecha. Contesta primero las que sepas."):rule("tiempo","Sin tiempo límite","Trata de avanzar a buen ritmo."))+
  rule("cierre","Al terminar una parte, ya no puedes regresar","Mientras sigas en ella, puedes cambiar tus respuestas.")+
  '</ul>'+
  '<p class="ask">¿Tienes dudas? Pregunta ahora a quien aplica la prueba.</p>'+
  '<button class="btn block" data-act="begin">Comenzar</button>'+salirFila()+'</div>';
}

/* ---- Intro de cada parte ---- */
function intro(){
  const m=meta(); EX={v:m.type==="multi2"?[]:m.type==="num"?"":m.type==="series"?["",""]:null,checked:false};SLOT=0;
  return '<div class="sheet"><div class="pnum" data-hold="menu"><b>'+(S.si+1)+'</b><span>de '+META.length+'</span></div><h1>'+esc(m.title)+'</h1>'+
  '<p>'+esc(m.howto)+'</p>'+
  '<div class="facts"><div class="fact"><b>'+ITEMS[m.id].length+'</b> preguntas</div>'+(S.timed?'<div class="fact">Tiempo: <b>'+fmtT(timeFor(m))+'</b></div>':'')+'</div>'+
  '<div class="exbox" id="exbox">'+exampleHTML()+'</div>'+
  '<button class="btn block" data-act="startSeries">Empezar parte '+(S.si+1)+'</button>'+
  (fsEnabled()?'<button class="btn quiet block" id="fsbtn" data-act="fullscreen" style="margin-top:8px'+(fsActive()?';display:none':'')+'">Pantalla completa</button>':'')+salirFila()+'</div>';
}
function exampleHTML(){
  const m=meta(), e=ejemplo(m);
  let h='<div class="exhead">Ejemplo para practicar</div>'+qHTML(m,e,EX.v,"ex",EX.checked?e.key:undefined);
  const ready = m.type==="multi2"?EX.v.length===2 : m.type==="num"?EX.v!=="" : m.type==="series"?(EX.v[0]!==""&&EX.v[1]!==""):EX.v!=null;
  if(EX.checked){
    const ok=correct(m,EX.v,e.key);
    let sol="";
    if(m.type==="num") sol=" La respuesta es "+e.key+" "+e.unit+".";
    if(m.type==="series") sol=" Los números que siguen son "+e.key.join(" y ")+".";
    if(m.type==="scramble") sol=" Ordenada dice: «"+e.solved+"»";
    h+='<div class="fb '+(ok?"ok":"no")+'">'+(ok?"Correcto. Así se contesta.":"No es la respuesta correcta; está marcada en verde.")+sol+'</div>';
  }
  return h;
}

/* ---- Pregunta ---- */
function header(){
  const m=meta(), arr=ansArr(m.id);
  const segs=arr.map((v,i)=>'<i class="'+(i===S.ii&&S.phase==="item"?"cur":isAnswered(m,v)?"done":"")+'"></i>').join("");
  return '<header class="bar"><div class="bar-top"><div class="part" data-hold="menu">Parte '+(S.si+1)+' de '+META.length+'<small>'+esc(m.title)+'</small></div>'+
  '<div class="bar-der">'+salirBtn()+(S.timed?'<div class="timer" id="timer" aria-label="Tiempo restante">--:--</div>':'')+'</div></div><div class="segs" aria-hidden="true">'+segs+'</div></header>';
}
function item(){
  const m=meta(), it=items()[S.ii], v=ansArr(m.id)[S.ii], n=items().length, last=S.ii===n-1;
  return header()+'<main class="q"><div class="qnum">Pregunta '+(S.ii+1)+' de '+n+'</div>'+qHTML(m,it,v,"real")+'</main>'+
  '<nav class="foot"><button class="btn ghost" data-act="prev"'+(S.ii===0?" disabled":"")+'>Anterior</button>'+
  '<button class="btn quiet" data-act="toReview">Ver todas</button>'+
  '<button class="btn" data-act="next">'+(last?"Revisar":"Siguiente")+'</button></nav>';
}

/* Constructor de la pregunta por tipo. showKey: para marcar la correcta en el ejemplo */
function qHTML(m,it,v,ctx,showKey){
  const sk=showKey!==undefined;
  const cls=(i,sel)=>{let c="opt";if(sk){const k=showKey;const isK=Array.isArray(k)?k.includes(i):k===i;if(isK)c+=" is-right";else if(sel)c+=" is-wrong";}return c;};
  const stem=it.stem?'<p class="stem">'+esc(it.stem)+'</p>':"";
  switch(m.type){
    case "single":{
      const o=it.options.map((t,i)=>'<button class="'+cls(i,v===i)+'" data-act="pick" data-ctx="'+ctx+'" data-v="'+i+'" aria-pressed="'+(v===i)+'"><span class="bub">'+LETTERS[i]+'</span><span>'+esc(t)+'</span></button>').join("");
      return (m.enunciado?'<p class="stem">'+esc(m.enunciado)+'</p>':stem)+'<div class="opts'+(it.options.length>4?" two":"")+'">'+o+'</div>';
    }
    case "multi2":{
      const sel=v||[];
      const o=it.options.map((t,i)=>'<button class="'+cls(i,sel.includes(i))+' sq" data-act="toggle" data-ctx="'+ctx+'" data-v="'+i+'" aria-pressed="'+sel.includes(i)+'"><span class="bub">'+LETTERS[i]+'</span><span>'+esc(t)+'</span></button>').join("");
      return stem+'<p class="counter" id="cnt-'+ctx+'">Elegiste '+sel.length+' de 2</p><div class="opts">'+o+'</div>';
    }
    case "figura":{
      /* Matriz (celdas, con null en la que falta) o lienzo con hueco, y opciones dibujadas en SVG numeradas desde 1. */
      const svg=(c,vb)=>'<svg viewBox="'+(vb||"0 0 100 100")+'" aria-hidden="true" focusable="false">'+(c||"")+'</svg>';
      const mat=it.lienzo?'<div class="lienzo">'+svg(it.lienzo,it.vista)+'</div>'
        :'<div class="matriz m'+Math.round(Math.sqrt(it.celdas.length))+'">'+it.celdas.map(c=>c==null?'<div class="celda falta" role="img" aria-label="Casilla que falta">?</div>':'<div class="celda">'+svg(c)+'</div>').join("")+'</div>';
      const o=it.opciones.map((t,i)=>'<button class="'+cls(i,v===i)+' fig" data-act="pick" data-ctx="'+ctx+'" data-v="'+i+'" aria-pressed="'+(v===i)+'" aria-label="Opción '+(i+1)+'"><span class="bub">'+(i+1)+'</span>'+svg(t)+'</button>').join("");
      return mat+'<div class="figs n'+it.opciones.length+'">'+o+'</div>';
    }
    case "pair":{
      return '<div class="pair"><span class="w">'+esc(it.a)+'</span><span class="amp">y</span><span class="w">'+esc(it.b)+'</span></div>'+
      '<div class="big2">'+[[1,"=","Significan lo mismo"],[0,"≠","Significan lo contrario"]].map(([val,sym,lab])=>'<button class="'+cls(val,v===val)+'" data-act="pick" data-ctx="'+ctx+'" data-v="'+val+'" aria-pressed="'+(v===val)+'"><span class="bub" aria-hidden="true">'+sym+'</span><span>'+lab+'</span></button>').join("")+'</div>';
    }
    case "yesno":
    case "scramble":{
      const labs=m.type==="yesno"?[[1,"Sí"],[0,"No"]]:[[1,"Verdadero"],[0,"Falso"]];
      const top=m.type==="scramble"?'<div class="chips">'+it.words.map(w=>'<span class="chip">'+esc(w)+'</span>').join("")+'</div><p class="hint">Ordena las palabras en tu mente. Lo que dice la frase, ¿es verdadero o falso?</p>':stem;
      return top+'<div class="big2">'+labs.map(([val,lab])=>'<button class="'+cls(val,v===val)+'" data-act="pick" data-ctx="'+ctx+'" data-v="'+val+'" aria-pressed="'+(v===val)+'"><span class="bub" aria-hidden="true">'+lab[0]+'</span><span>'+lab+'</span></button>').join("")+'</div>';
    }
    case "num":{
      const val=v||"";
      const right = sk ? ' style="border-color:'+(numEq(val,showKey)?"var(--ok)":"var(--bad)")+'"' : "";
      return stem+'<div class="ansline"><div class="slot act"'+right+'>'+(val?esc(val):'<span class="ph">0</span>')+(sk?"":'<span class="caret"></span>')+'</div>'+(it.unit?'<span class="unit">'+esc(it.unit)+'</span>':"")+'</div>'+(sk?"":keypad(ctx));
    }
    case "series":{
      const val=v||["",""];
      const slots=[0,1].map(j=>{
        let st=""; if(sk) st=' style="border-color:'+(numEq(val[j],showKey[j])?"var(--ok)":"var(--bad)")+'"';
        return '<button class="slot'+(!sk&&SLOT===j?" act":"")+'" data-act="slot" data-ctx="'+ctx+'" data-v="'+j+'"'+st+' aria-label="Número '+(j+1)+'">'+(val[j]?esc(val[j]):'<span class="ph">?</span>')+(!sk&&SLOT===j?'<span class="caret"></span>':"")+'</button>';
      }).join("");
      return '<p class="stem">¿Qué dos números siguen?</p><div class="terms">'+it.terms.map(t=>'<span class="term">'+esc(t)+'</span>').join("")+slots+'</div>'+(sk?"":keypad(ctx));
    }
  }
  return "";
}
function keypad(ctx){
  const k=["1","2","3","4","5","6","7","8","9",".","0","del"];
  const m=meta(), okLab = m.type==="series"&&SLOT===0 ? "Siguiente número" : "Listo";
  return '<div class="keypad">'+k.map(x=>'<button data-act="key" data-ctx="'+ctx+'" data-v="'+x+'" '+(x==="del"?'class="fn" aria-label="Borrar"':'')+(x==="."?' aria-label="Punto decimal"':'')+'>'+(x==="del"?"Borrar":x)+'</button>').join("")+
  '<button class="ok" data-act="key" data-ctx="'+ctx+'" data-v="ok">'+okLab+'</button></div>';
}
function scheduleNext(ms){
  const tok=++advanceTok, here=S.si+":"+S.ii;
  setTimeout(()=>{if(tok===advanceTok&&S.phase==="item"&&here===S.si+":"+S.ii)next();},ms);
}

/* ---- Revisión de la parte ---- */
function etiquetaFinParte(){return S.si<META.length-1?"Continuar con la parte "+(S.si+2):"Terminar la prueba";}
function review(){
  const m=meta(), arr=ansArr(m.id), miss=arr.filter(v=>!isAnswered(m,v)).length;
  return header()+'<main class="q"><h1>Revisa la parte '+(S.si+1)+'</h1>'+
  '<p>'+(miss?'Te faltan <b>'+miss+'</b> '+(miss===1?"pregunta":"preguntas")+'. Toca un número para ir a ella.':'Contestaste todas. Toca un número si quieres cambiar alguna.')+'</p>'+
  '<div class="grid">'+arr.map((v,i)=>'<button class="'+(isAnswered(m,v)?"done":"")+'" data-act="goto" data-v="'+i+'" aria-label="Pregunta '+(i+1)+(isAnswered(m,v)?", contestada":", sin contestar")+'">'+(i+1)+'</button>').join("")+'</div>'+
  '<p class="small muted">Azul: contestada. Blanco: sin contestar.</p></main>'+
  '<nav class="foot rv"><button class="btn ghost" data-act="goto" data-v="'+(arr.length-1)+'">Volver</button><button class="btn" data-act="endSeries">'+etiquetaFinParte()+'</button></nav>';
}
function timeout(){
  return '<div class="sheet"><h1 data-hold="menu">Se terminó el tiempo de la parte '+(S.si+1)+'</h1><p>Tus respuestas quedaron guardadas. Sigue con la siguiente parte.</p><button class="btn block" data-act="nextSeries">Continuar</button>'+salirFila()+'</div>';
}
function done(){
  return '<div class="sheet">'+brand()+'<h1>Terminaste la prueba</h1><p>Gracias'+(S.cand.nombre?", "+esc(S.cand.nombre.split(/\s+/)[0]):"")+', por tu tiempo y tu esfuerzo. Entrega el dispositivo a la persona que aplica la prueba.</p>'+
  '<div style="margin-top:40px"><p class="small muted">Solo para quien aplica la prueba</p>'+(S.sesion&&MENU?'<button class="hold" id="hold" data-hold="volver"><i></i><span>Mantén presionado para volver al menú de pruebas</span></button>':'<button class="hold" id="hold" data-hold="results"><i></i><span>Mantén presionado para ver resultados</span></button>')+'</div></div>';
}

/* ====== Calificación ====== */
function scoreAll(){
  return META.map(m=>{
    const arr=S.ans[m.id]||ITEMS[m.id].map(()=>null), k=KEY[m.id];
    let ok=0,err=0,om=0; const st=arr.map((v,i)=>{const c=correct(m,v,k[i]);if(c===null){om++;return "omitida";}if(c){ok++;return "ok";}err++;return "error";});
    const max=ITEMS[m.id].length*m.weight;
    const pts=m.rule==="neto"?Math.max(0,ok-err):ok*m.weight;
    const t=S.times[m.id]||{};
    return {m,arr,st,ok,err,om,pts,max,pct:Math.round(pts/max*100),used:t.start?(t.end||now())-t.start:0,timedOut:!!t.timedOut};
  });
}
/* Indicadores de proceso por serie, a partir de S.log. null si la serie no tiene registro.
   Respuesta rápida: primera respuesta en menos de RAPIDA_MS con el reactivo en pantalla.
   Umbral interno y provisional; se calibra con la aplicación piloto sin límite. */
const RAPIDA_MS = 2000;
/* Registro de una serie. Sin S.log la aplicación viene de una versión anterior; una serie no presentada queda vacía. */
function logOf(id){return S.log?(S.log[id]||(S.times[id]?null:[])):null;}
function proc(x){
  const lg=logOf(x.m.id);
  if(!lg) return null;
  const k=KEY[x.m.id], fs=[], p={rap:0,rapErr:0,chOk:0,chErr:0,chOtro:0,omVista:0,omNoVista:0,incompleto:false};
  x.st.forEach((st,i)=>{
    const r=lg[i];
    if(st==="omitida"){if(r&&r.d>0)p.omVista++;else p.omNoVista++;return;}
    if(!r||r.f==null){p.incompleto=true;return;}
    fs.push(r.f);
    const primeraOk=correct(x.m,r.a,k[i]);
    if(r.f<RAPIDA_MS){p.rap++;if(!primeraOk)p.rapErr++;}
    if(r.c>0){if(!primeraOk&&st==="ok")p.chOk++;else if(primeraOk&&st==="error")p.chErr++;else p.chOtro++;}
  });
  fs.sort((a,b)=>a-b);
  const n=fs.length;
  p.med=n?(n%2?fs[n>>1]:(fs[n/2-1]+fs[n/2])/2):null;
  return p;
}
const seg = ms => (ms/1000).toFixed(1)+" s";
function fmtProc(x,i,it){
  const lg=logOf(x.m.id);
  if(!lg) return "sin registro | sin registro";
  const r=lg[i];
  if(x.st[i]==="omitida") return (r&&r.d>0?"vista, sin respuesta":"no vista")+" | 0";
  if(!r||r.f==null) return "sin registro | sin registro";
  return seg(r.f)+" | "+(r.c?r.c+" (primera: "+fmtAns(x.m,it,r.a,i)+")":"0");
}
function fmtFig(m,i,v){const d=desc(m,i);return "opción "+(v+1)+(d&&d.opciones?" ("+d.opciones[v]+")":"");}
function fmtAns(m,it,v,i){
  if(!isAnswered(m,v)) return "(sin respuesta)";
  switch(m.type){
    case "figura": return fmtFig(m,i,v);
    case "single": return LETTERS[v].toLowerCase()+") "+it.options[v];
    case "multi2": return [...v].sort().map(i=>LETTERS[i].toLowerCase()+") "+it.options[i]).join(" + ")+(v.length<2?" (solo eligió una)":"");
    case "pair": return v===1?"Lo mismo":"Lo contrario";
    case "yesno": return v===1?"Sí":"No";
    case "scramble": return v===1?"Verdadero":"Falso";
    case "num": return v+(it.unit?" "+it.unit:"");
    case "series": return (v[0]||"_")+", "+(v[1]||"_");
  }
}
function fmtKey(m,it,k,i){
  switch(m.type){
    case "figura": return fmtFig(m,i,k);
    case "single": return LETTERS[k].toLowerCase()+") "+it.options[k];
    case "multi2": return k.map(i=>LETTERS[i].toLowerCase()+") "+it.options[i]).join(" + ");
    case "pair": return k===1?"Lo mismo":"Lo contrario";
    case "yesno": return k===1?"Sí":"No";
    case "scramble": return k===1?"Verdadero":"Falso";
    case "num": return k+(it.unit?" "+it.unit:"");
    case "series": return k.join(", ");
  }
}
function fmtStem(m,it,i){
  switch(m.type){
    case "figura": {const d=desc(m,i);return d&&d.regla?"regla: "+d.regla:"(figuras)";}
    case "pair": return it.a+" / "+it.b;
    case "scramble": return "«"+it.words.join(" ")+"»";
    case "series": return it.terms.join(" ")+" _ _";
    case "single": if(!it.stem) return it.options.map((o,i)=>LETTERS[i].toLowerCase()+") "+o).join("  ");
      return it.stem+"  ["+it.options.map((o,i)=>LETTERS[i].toLowerCase()+") "+o).join("  ")+"]";
    case "multi2": return it.stem+"  ["+it.options.map((o,i)=>LETTERS[i].toLowerCase()+") "+o).join("  ")+"]";
    default: return it.stem;
  }
}
function buildPrompt(sc){
  const c=S.cand, d=new Date(S.startedAt||now());
  const tot=sc.reduce((a,x)=>a+x.pts,0), max=sc.reduce((a,x)=>a+x.max,0);
  const dur=(S.finishedAt||now())-(S.startedAt||now());
  const L=[];
  L.push("# Calificación de la "+TEST_NAME+" ("+COMPANY_LEGAL+")","");
  L.push("## Rol","Actúa como psicólogo(a) laboral especializado(a) en evaluación psicométrica que apoya el proceso de reclutamiento de "+COMPANY_LEGAL+", "+COMPANY_DESC+". La empresa contrata personal de campo, empaque, taller y mantenimiento, logística y administración. Califica e interpreta la prueba descrita abajo usando exclusivamente los datos de este mensaje.","");
  L.push("## Datos de la aplicación");
  L.push("- Candidato: "+(c.nombre||"(no registrado)"));
  L.push("- Edad: "+(c.edad||"(no registrada)")+" (solo para identificar al candidato; ver Restricciones)");
  L.push("- Escolaridad terminada: "+(c.esc||"(no registrada)"));
  L.push("- Años desde que dejó la escuela: "+(c.anos||"(no registrado)"));
  L.push("- Uso de teléfono o tablet, según el aplicador: "+(c.disp?c.disp.toLowerCase():"(no registrado)"));
  L.push("- Puesto al que aspira: "+(c.puesto||"(no registrado)"));
  L.push("- Rancho o área: "+(c.sede||"(no registrado)"));
  L.push("- Aplicador: "+(c.aplic||"(no registrado)"));
  L.push("- Fecha y hora de inicio: "+d.toLocaleString("es-MX",{dateStyle:"long",timeStyle:"short"}));
  L.push("- Modalidad: digital en tablet o teléfono, respuesta por toque; tiempo límite por serie: "+(S.timed?"sí":"no, aplicación piloto (solo se registró el tiempo)"));
  L.push("- Tipo de puesto: "+(MODES[S.mode]?MODES[S.mode].puesto:"(no registrado)")+"; modalidad de tiempo: "+(S.timed?((MODES[S.mode]||MODES.std).label.toLowerCase()+((S.mode==="ext")?" ("+MODES.ext.factor+" veces la estándar)":"")):"sin límite"));
  L.push("- Duración total: "+fmt(dur)+" (min:s)");
  L.push("- Estado de la aplicación: "+(S.status==="cancelada"?"cancelada por el aplicador durante la parte "+(S.si+1)+"; las series no presentadas cuentan como omitidas y deben reportarse como no evaluadas":"terminada"));
  L.push(lineaIncidencias(S.incid),"");
  L.push("## Descripción de la prueba",PROMPT.descripcion,"");
  L.push("| Serie | Nombre | Factor | Reactivos | Regla de puntaje | Máximo | Límite |","|---|---|---|---|---|---|---|");
  sc.forEach(x=>L.push("| "+x.m.id+" | "+x.m.name+" | "+x.m.factor+" | "+ITEMS[x.m.id].length+" | "+reglaTexto(x.m)+" | "+x.max+" | "+(S.timed?fmt(((S.times[x.m.id]&&S.times[x.m.id].limit)||timeFor(x.m))*1000):"sin límite")+" |"));
  L.push("| Total | | | "+META.reduce((a,m)=>a+ITEMS[m.id].length,0)+" | | "+max+" | |","");
  L.push("## Reglas de calificación",...PROMPT.reglas,"");
  L.push(...PROMPT.escala);
  L.push("## Precalificación automática","Calculada por la aplicación con la clave y las reglas anteriores.","");
  L.push("| Serie | Factor | Aciertos | Errores | Omisiones | Puntaje | Máximo | % | Tiempo usado | Se agotó el tiempo |","|---|---|---|---|---|---|---|---|---|---|");
  sc.forEach(x=>L.push("| "+x.m.id+" | "+x.m.factor+" | "+x.ok+" | "+x.err+" | "+x.om+" | "+x.pts+" | "+x.max+" | "+x.pct+" | "+fmt(x.used)+" | "+(S.timed?(x.timedOut?"sí":"no"):"n/a")+" |"));
  L.push("| Total | | "+sc.reduce((a,x)=>a+x.ok,0)+" | "+sc.reduce((a,x)=>a+x.err,0)+" | "+sc.reduce((a,x)=>a+x.om,0)+" | "+tot+" | "+max+" | "+Math.round(tot/max*100)+" | "+fmt(sc.reduce((a,x)=>a+x.used,0))+" | |","");
  const pr=sc.map(proc);
  L.push("## Indicadores de proceso");
  if(pr.every(p=>!p)) L.push("Esta aplicación no registró tiempos por reactivo porque se inició con una versión anterior de la prueba. Omite el análisis de tiempos por reactivo y de cambios de respuesta.","");
  else{
    L.push("Registrados por la aplicación durante la prueba.","- Primera respuesta: tiempo acumulado con el reactivo en pantalla hasta la primera respuesta del candidato. No cuenta el tiempo en otras pantallas ni con la pantalla apagada.","- Respuesta rápida: primera respuesta en menos de "+(RAPIDA_MS/1000)+" s. Umbral interno y provisional, sin calibrar con población propia.","- Cambios: se comparan la primera respuesta y la final. Otros cambios son los que no alteraron el resultado.","- Omisiones vistas: el reactivo apareció en pantalla y quedó sin respuesta. No vistas: el candidato nunca llegó a él.","- Precisión: aciertos entre reactivos contestados.","");
    L.push("| Serie | Factor | Mediana de primera respuesta | Rápidas | Rápidas con primera respuesta errónea | Cambios de error a acierto | Cambios de acierto a error | Otros cambios | Omisiones vistas | Omisiones no vistas | Precisión % | % del límite usado |","|---|---|---|---|---|---|---|---|---|---|---|---|");
    sc.forEach((x,j)=>{
      const p=pr[j], lim=S.timed&&S.times[x.m.id]&&S.times[x.m.id].limit, prec=x.ok+x.err?Math.round(x.ok/(x.ok+x.err)*100):"n/a", usoLim=lim?Math.round(x.used/(lim*1000)*100):"n/a";
      if(!p){L.push("| "+x.m.id+" | "+x.m.factor+" | sin registro | | | | | | | | "+prec+" | "+usoLim+" |");return;}
      L.push("| "+x.m.id+(p.incompleto?" (registro incompleto)":"")+" | "+x.m.factor+" | "+(p.med==null?"n/a":seg(p.med))+" | "+p.rap+" | "+p.rapErr+" | "+p.chOk+" | "+p.chErr+" | "+p.chOtro+" | "+p.omVista+" | "+p.omNoVista+" | "+prec+" | "+usoLim+" |");
    });
    L.push("");
  }
  L.push("## Respuestas reactivo por reactivo",META.some(m=>m.type==="figura")
    ?"Formato: reactivo | regla que resuelve el reactivo | respuesta del candidato | clave | resultado | primera respuesta | cambios de respuesta. Las opciones se numeran desde 1 en el orden en que se mostraron; entre paréntesis va la descripción de la figura elegida."
    :"Formato: reactivo | enunciado [opciones] | respuesta del candidato | clave | resultado | primera respuesta | cambios de respuesta. Las letras corresponden al orden en que se mostraron las opciones.","");
  sc.forEach(x=>{
    L.push("### Serie "+x.m.id+": "+x.m.name);
    ITEMS[x.m.id].forEach((it,i)=>L.push(x.m.id+"-"+String(i+1).padStart(2,"0")+" | "+fmtStem(x.m,it,i)+" | "+fmtAns(x.m,it,x.arr[i],i)+" | "+fmtKey(x.m,it,KEY[x.m.id][i],i)+" | "+x.st[i]+" | "+fmtProc(x,i,it)));
    L.push("");
  });
  L.push(...PROMPT.tareas);
  L.push(...PROMPT.formato);
  L.push(...PROMPT.restricciones);
  return L.join("\n");
}
function results(){
  const sc=scoreAll(), tot=sc.reduce((a,x)=>a+x.pts,0), max=sc.reduce((a,x)=>a+x.max,0);
  S._prompt=buildPrompt(sc);
  return '<div class="sheet">'+brand()+'<p class="muted small">Resultados para el aplicador</p><h1>'+esc(S.cand.nombre||"Candidato")+'</h1>'+
  '<p>Puntaje preliminar: <b>'+tot+' de '+max+'</b> ('+Math.round(tot/max*100)+'%). Duración: '+fmt((S.finishedAt||now())-S.startedAt)+'. Modalidad: '+(S.timed?(MODES[S.mode]||MODES.std).label.toLowerCase():"sin límite (piloto)")+'.</p>'+
  '<div class="tscroll"><table class="sum"><thead><tr><th>Parte</th><th>Bien</th><th>Mal</th><th>Omit.</th><th>Puntos</th><th>Tiempo</th></tr></thead><tbody>'+
  sc.map(x=>'<tr><td><b>'+x.m.id+'</b><small>'+esc(x.m.factor)+'</small></td><td>'+x.ok+'</td><td>'+x.err+'</td><td>'+x.om+'</td><td>'+x.pts+'/'+x.max+'</td><td>'+fmt(x.used)+(x.timedOut?"*":"")+'</td></tr>').join("")+
  '</tbody><tfoot><tr><td>Total</td><td></td><td></td><td></td><td>'+tot+'/'+max+'</td><td></td></tr></tfoot></table></div>'+
  (sc.some(x=>x.timedOut)?'<p class="small muted">* Se agotó el tiempo en esa parte.</p>':'')+
  '<label class="f" style="margin-top:18px"><span>Incidencias de la aplicación <small class="muted">(opcional)</small></span><textarea id="f-incid" rows="3" maxlength="1000" placeholder="Interrupciones, ruido, olvidó sus lentes, pidió ayuda, falla del dispositivo">'+esc(S.incid)+'</textarea></label>'+
  '<p class="small muted">Se agregan al prompt. Anota hechos observados, no opiniones sobre el candidato.</p>'+
  '<h2>Prompt para la IA</h2><p class="muted small">Cópialo y pégalo en Claude para obtener la calificación e interpretación completas. Contiene la clave de respuestas: no lo compartas con el candidato.</p>'+
  '<div class="row" style="margin-bottom:12px"><button class="btn" data-act="copy">Copiar prompt</button>'+(navigator.share?'<button class="btn ghost" data-act="share">Compartir</button>':'')+'<button class="btn ghost" data-act="download">Descargar .txt</button></div>'+
  '<pre class="prompt" id="prompt">'+esc(S._prompt)+'</pre>'+
  '<button class="btn quiet block" style="margin-top:18px" data-act="newTest">'+(S._archived?"Volver":"Nueva aplicación")+'</button></div>';
}

/* ====== Flujo ====== */
function startSeries(){
  const m=meta();ansArr(m.id);
  const lim=S.timed?timeFor(m):null;
  S.times[m.id]={start:now(),limit:lim,mode:S.mode||"std",deadline:lim?now()+lim*1000:null};
  if(!S.log)S.log={};if(!S.log[m.id])S.log[m.id]=ITEMS[m.id].map(()=>null);
  S.ii=0;SLOT=0;S.phase="item";save();render();
}
function finishSeries(byTime){
  leaveView();
  const m=meta();const t=S.times[m.id]||(S.times[m.id]={start:now()});
  if(!t.end){t.end=byTime&&t.deadline?t.deadline:now();t.timedOut=!!byTime;}
  S.phase=byTime?"timeout":"_";
  if(!byTime) nextSeries(); else {save();render();}
}
function nextSeries(){
  S.si++;S.ii=0;
  if(S.si>=META.length){S.si=META.length-1;S.phase="done";S.status="terminada";S.finishedAt=now();}
  else S.phase="intro";
  save();if(S.phase==="done"){archivePut(S);registrarEnSesion();}render();
}
function goItem(i){S.ii=i;SLOT=0;S.phase="item";save();render();}
function next(){const n=items().length;if(S.ii<n-1)goItem(S.ii+1);else{S.phase="review";save();render();}}

function setVal(ctx,val){
  if(ctx==="ex"){EX.v=val;$("#exbox").innerHTML=exampleHTML();return;}
  ansArr(meta().id)[S.ii]=val;save();
}
function getVal(ctx){return ctx==="ex"?EX.v:ansArr(meta().id)[S.ii];}

/* ====== Temporizador ====== */
function tick(){
  if(BLOCKED)return;
  if(!S.timed||!(S.phase==="item"||S.phase==="review"))return;
  const t=S.times[meta().id];if(!t||!t.deadline)return;
  const left=t.deadline-now();
  if(left<=0){finishSeries(true);return;}
  const el=$("#timer");if(el){el.textContent=fmt(left);el.classList.toggle("low",left<=30000);}
}
setInterval(tick,250);

/* ====== Eventos ====== */
document.addEventListener("click",e=>{
  if(BLOCKED)return;
  const b=e.target.closest("[data-act]");if(!b||b.disabled)return;
  const act=b.dataset.act, ctx=b.dataset.ctx, v=b.dataset.v;
  const m=S.phase==="setup"?null:meta();
  switch(act){
    case "mode": S.mode=v;document.querySelectorAll('[data-act="mode"]').forEach(x=>x.setAttribute("aria-pressed",x===b));break;
    case "timed": S.timed=v==="1";document.querySelectorAll('[data-act="timed"]').forEach(x=>x.setAttribute("aria-pressed",x===b));break;
    case "resume": {const r=S._resume;S=r;delete S._resume;if(S.phase==="results")S.phase="done";save();render();if(S.phase!=="done")wake();break;}
    case "discard": modal("¿Descartar la prueba sin terminar?","Se perderán las respuestas de esa aplicación.",[{label:"Cancelar",cls:"ghost"},{label:"Descartar",fn:()=>{clearStore();S=blank();render();}}]);break;
    case "toWelcome": readSetup();
      if(!S.cand.nombre){toast("Escribe el nombre del candidato");$("#f-nombre").focus();return;}
      if(!S.mode){toast("Elige el tipo de puesto");return;}
      {const ex=load();if(ex&&ex.id!==S.id&&["welcome","intro","item","review","timeout"].includes(ex.phase)&&!S._resume){modal("Hay otra prueba en curso","La prueba de "+(ex.cand&&ex.cand.nombre||"otro candidato")+" sigue abierta en este dispositivo. Recarga la página para continuarla.",[{label:"Entendido"}]);return;}}
      if(S._resume)archivePut(S._resume);
      S.phase="welcome";delete S._resume;save();render();wake();break;
    case "logo": b.replaceWith(b.cloneNode(true)); break;
    case "begin": S.startedAt=now();S.si=0;S.phase="intro";save();render();fullscreen();break;
    case "startSeries": startSeries();break;
    case "fullscreen": fullscreen();break;
    case "exCheck": EX.checked=true;$("#exbox").innerHTML=exampleHTML();break;
    case "pick":{
      const val=+v;
      if(ctx==="ex"){if(EX.checked&&m.type!=="multi2")EX.checked=false;EX.v=val;EX.checked=true;$("#exbox").innerHTML=exampleHTML();break;}
      setVal(ctx,val);commitAns(m.id,S.ii);render();scheduleNext(320);
      break;}
    case "toggle":{
      advanceTok++;
      let cur=[...(getVal(ctx)||[])];const i=+v;
      if(cur.includes(i))cur=cur.filter(x=>x!==i);
      else if(cur.length>=2){const c=document.getElementById("cnt-"+ctx);if(c){c.textContent="Ya elegiste 2. Toca una para quitarla.";c.classList.add("nudge");}return;}
      else cur.push(i);
      if(ctx==="ex"){EX.checked=cur.length===2;EX.v=cur;$("#exbox").innerHTML=exampleHTML();}
      else{setVal(ctx,cur);if(cur.length===2)commitAns(m.id,S.ii);render();if(cur.length===2)scheduleNext(550);}
      break;}
    case "slot": SLOT=+v; if(ctx==="ex")$("#exbox").innerHTML=exampleHTML(); else render(); break;
    case "key": keyInput(ctx,v);break;
    case "prev": if(S.ii>0)goItem(S.ii-1);break;
    case "next": advanceTok++;next();break;
    case "toReview": advanceTok++;S.phase="review";save();render();break;
    case "goto": goItem(+v);break;
    case "endSeries":{
      const arr=ansArr(m.id),miss=arr.filter(x=>!isAnswered(m,x)).length;
      const go=()=>finishSeries(false);
      if(miss)modal("Te faltan "+miss+" "+(miss===1?"pregunta":"preguntas"),"Si terminas la parte ya no podrás regresar a ella.",[{label:"Seguir contestando",cls:"ghost"},{label:etiquetaFinParte(),fn:go}]);
      else modal("¿Terminar la parte "+(S.si+1)+"?","Ya no podrás regresar a ella.",[{label:"Revisar otra vez",cls:"ghost"},{label:etiquetaFinParte(),fn:go}]);
      break;}
    case "nextSeries": nextSeries();break;
    case "copy": copyText(S._prompt);break;
    case "share": navigator.share({title:"Resultados "+(S.cand.nombre||""),text:S._prompt}).catch(e=>{if(!e||e.name!=="AbortError")copyText(S._prompt);});break;
    case "download": download();break;
    case "newTest":
      if(S._archived){S=blank();render();break;}
      modal("¿Iniciar una nueva aplicación?","Estos resultados quedan en el historial de este dispositivo.",[{label:"Cancelar",cls:"ghost"},{label:"Nueva aplicación",fn:()=>{archivePut(S);clearStore();S=blank();render();}}]);break;
    case "openArch":{const h=archiveLoad().find(x=>x.id===v);if(!h)break;S=h;S._archived=true;S.phase="results";render();break;}
    case "clearArch": modal("¿Borrar el historial?","Se eliminarán del dispositivo los resultados de todas las aplicaciones anteriores. No se puede deshacer.",[{label:"Cancelar",cls:"ghost"},{label:"Borrar historial",fn:()=>{try{localStorage.removeItem(ARCH);}catch(e){}render();}}]);break;
  }
});
function keyInput(ctx,k){
  const m=meta();let v=getVal(ctx);
  if(k==="ok"){
    if(m.type==="series"&&SLOT===0){SLOT=1;if(ctx==="ex")$("#exbox").innerHTML=exampleHTML();else{const y=window.scrollY;render();window.scrollTo(0,y);}return;}
    if(ctx==="ex"){const ready=m.type==="num"?(v||"")!=="":(v&&v[0]!==""&&v[1]!=="");if(ready){EX.checked=true;$("#exbox").innerHTML=exampleHTML();}else toast("Escribe tu respuesta");return;}
    if(m.type==="series"&&(!v||(v[0]||"")===""||(v[1]||"")==="")){const miss=!v||(v[0]||"")===""?0:1;SLOT=miss;const y=window.scrollY;render();window.scrollTo(0,y);toast("Falta escribir un número");return;}
    if(m.type==="num"&&!(v||"")){toast("Escribe tu respuesta");return;}
    commitAns(m.id,S.ii);advanceTok++;next();return;
  }
  const edit=s=>{s=s||"";if(k==="del")return s.slice(0,-1);if(k==="."){if(s.includes("."))return s;return (s===""?"0":s)+".";}if(s.length>=9)return s;if(s==="0")return k;return s+k;};
  if(m.type==="num"){v=edit(v);}
  else{v=[...(v||["",""])];v[SLOT]=edit(v[SLOT]);}
  if(ctx==="ex"){EX.v=v;EX.checked=false;$("#exbox").innerHTML=exampleHTML();}
  else{setVal(ctx,v);const y=window.scrollY;render();window.scrollTo(0,y);}
}
document.addEventListener("keydown",e=>{
  if(S.phase!=="item"&&S.phase!=="intro")return;
  if(e.target.matches("input,select,textarea"))return;
  const m=meta();
  if(m.type==="num"||m.type==="series"){
    let k=null;if(/^[0-9]$/.test(e.key))k=e.key;else if(e.key==="."||e.key===",")k=".";else if(e.key==="Backspace")k="del";else if(e.key==="Enter")k="ok";
    if(k){e.preventDefault();keyInput(S.phase==="intro"?"ex":"real",k);return;}
    if(m.type==="series"&&e.key==="Tab"&&S.phase==="item"){e.preventDefault();SLOT=SLOT?0:1;render();return;}
  }
  if(m.type==="figura"&&/^[1-8]$/.test(e.key)){
    const b=document.querySelector('[data-act=pick][data-ctx="'+(S.phase==="intro"?"ex":"real")+'"][data-v="'+(+e.key-1)+'"]');
    if(b){e.preventDefault();b.click();return;}
  }
  if(S.phase==="item"){
    if(e.key==="ArrowRight"||e.key==="Enter"){e.preventDefault();advanceTok++;next();}
    if(e.key==="ArrowLeft"&&S.ii>0){e.preventDefault();goItem(S.ii-1);}
  }
});

/* Incidencias del aplicador: actualizan el prompt y se guardan con la aplicación */
let incidT=null;
document.addEventListener("input",e=>{
  if(e.target.id!=="f-incid"||S.phase!=="results")return;
  S.incid=e.target.value;
  S._prompt=buildPrompt(scoreAll());const pre=$("#prompt");if(pre)pre.textContent=S._prompt;
  save();
  clearTimeout(incidT);const st=S;incidT=setTimeout(()=>archivePut(st),400);
});

/* Pulsación larga: ver resultados (1.5 s) y menú del aplicador (3 s, desde "Salir" o el título) */
let holdT=null,holdStart=0,holdEl=null;
function holdStep(){
  if(!holdEl||!document.body.contains(holdEl)){holdT=null;return;}
  const kind=holdEl.dataset.hold, ms=kind==="menu"?3000:1500, p=Math.min(1,(now()-holdStart)/ms);
  const bar=holdEl.querySelector("i");if(bar)bar.style.width=(p*100)+"%";
  if(p>=1){holdT=null;const el=holdEl;holdEl=null;if(bar)bar.style.width="0";
    if(kind==="results"){S.phase="results";save();render();}
    else if(kind==="volver") volverAlMenu();
    else applicatorMenu();
    return;}
  holdT=requestAnimationFrame(holdStep);
}
function holdCancel(){if(holdT){cancelAnimationFrame(holdT);holdT=null;}if(holdEl){const b=holdEl.querySelector("i");if(b)b.style.width="0";
  if(holdEl.classList.contains("salir"))toast("Solo quien aplica la prueba: mantén presionado 3 segundos");holdEl=null;}}
document.addEventListener("pointerdown",e=>{const el=e.target.closest("[data-hold]");if(!el)return;if(el.classList.contains("hold")||el.classList.contains("salir"))e.preventDefault();holdEl=el;holdStart=now();holdT=requestAnimationFrame(holdStep);});
["pointerup","pointercancel"].forEach(ev=>document.addEventListener(ev,holdCancel,true));
document.addEventListener("pointerleave",e=>{if(e.target===holdEl)holdCancel();},true);
document.addEventListener("contextmenu",e=>{if(e.target.closest("[data-hold]"))e.preventDefault();});
/* Cancela la aplicación en curso: cierra el reloj de la parte abierta, la archiva y limpia el estado. */
function cancelar(){
  leaveView();const t=S.times[meta().id];if(t&&t.start&&!t.end)t.end=now();
  S.status="cancelada";S.finishedAt=now();S.phase="done";save();archivePut(S);registrarEnSesion();clearStore();S=blank();
}
function applicatorMenu(){
  const btns=[{label:"Seguir con la prueba",cls:"ghost"}];
  if(MENU) btns.push({label:"Volver al menú de pruebas",cls:"ghost",fn:()=>modal("¿Cancelar y volver al menú?","El candidato ya no podrá continuar. Lo contestado queda en el historial de este dispositivo.",[{label:"No",cls:"ghost"},{label:"Sí, cancelar y volver",fn:()=>{
    cancelar();location.href="../";}}])});
  if(!(MENU&&S.sesion)) btns.push({label:"Cancelar aplicación",fn:()=>modal("¿Cancelar esta aplicación?","El candidato ya no podrá continuar.",[{label:"No",cls:"ghost"},{label:"Sí, cancelar",fn:()=>{
    cancelar();render();toast("Aplicación cancelada y guardada en el historial");}}])});
  modal("Menú del aplicador","Prueba de "+(S.cand.nombre||"sin nombre")+", parte "+(S.si+1)+" de "+META.length+". Si cancelas, lo contestado queda en el historial del dispositivo.",btns);
}

/* Otra pestaña con la misma prueba: bloquear esta */
window.addEventListener("storage",e=>{
  if(e.key!==STORE||BLOCKED||!e.newValue||S._archived||S.phase==="setup")return;
  const o=parseState(e.newValue);
  if(o&&o.tab&&o.tab!==TAB){BLOCKED=true;advanceTok++;showBlocked();}
});
window.addEventListener("pagehide",()=>{if(!["setup","results"].includes(S.phase))save();});

/* Copiar, descargar */
function copyText(t){
  const fallback=()=>{const ta=document.createElement("textarea");ta.value=t;ta.setAttribute("readonly","");ta.style.position="fixed";ta.style.opacity="0";document.body.appendChild(ta);ta.select();ta.setSelectionRange(0,t.length);let ok=false;try{ok=document.execCommand("copy");}catch(e){}ta.remove();toast(ok?"Prompt copiado":"No se pudo copiar; usa Descargar");};
  if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(()=>toast("Prompt copiado"),fallback);else fallback();
}
async function download(){
  const name=("amador-russell-resultados-"+(S.cand.nombre||"candidato")).normalize("NFD").replace(/[\u0300-\u036f]/g,"").replace(/[^a-zA-Z0-9]+/g,"-").toLowerCase()+".txt";
  if(window.claude&&typeof window.claude.use==="function"){
    let dl=null;try{dl=await window.claude.use("downloads");}catch(e){}
    if(!dl){toast("Descarga no disponible aquí; usa Copiar prompt");return;}
    try{await dl.save({filename:name,data:S._prompt});toast("Archivo guardado");}
    catch(e){if(e&&e.code==="declined")return;toast(e&&e.code==="rate_limited"?"Espera un momento y vuelve a intentar":"No se pudo descargar; usa Copiar prompt");}
    return;
  }
  const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([S._prompt],{type:"text/plain;charset=utf-8"}));a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},500);
}

/* Pantalla encendida y pantalla completa */
let wl=null;
async function wake(){try{if("wakeLock" in navigator&&!wl){wl=await navigator.wakeLock.request("screen");wl.addEventListener("release",()=>{wl=null;});}}catch(e){}}
document.addEventListener("visibilitychange",()=>{
  if(document.visibilityState==="hidden"){if(VIEW){checkpoint();VIEW.t=null;}}
  else{if(VIEW&&VIEW.t==null)VIEW.t=Date.now();if(S.phase!=="setup")wake();}
  tick();
});
/* Pantalla completa: iPad usa el prefijo webkit; en iPhone y dentro de marcos que no la permiten no existe y el botón no aparece */
function fsEnabled(){return !!(document.fullscreenEnabled||document.webkitFullscreenEnabled);}
function fsActive(){return !!(document.fullscreenElement||document.webkitFullscreenElement);}
function fullscreen(){const d=document.documentElement;if(fsActive())return;try{const p=d.requestFullscreen?d.requestFullscreen():d.webkitRequestFullscreen?d.webkitRequestFullscreen():null;if(p&&p.catch)p.catch(()=>{});}catch(e){}}
function fsSync(){const b=$("#fsbtn");if(b)b.style.display=fsActive()?"none":"";}
document.addEventListener("fullscreenchange",fsSync);
document.addEventListener("webkitfullscreenchange",fsSync);
window.addEventListener("beforeunload",e=>{if(["intro","item","review","timeout"].includes(S.phase)){e.preventDefault();e.returnValue="";}});

/* Registra en la sesión del menú el resultado de esta prueba, con su prompt.
   Una cancelación antes de comenzar (prueba abierta por error) no se registra: queda pendiente. */
function registrarEnSesion(){
  if(!MENU||!S.sesion) return true;
  if(S.status==="cancelada"&&!S.startedAt) return true;
  const s=sesionLeer();if(!s||s.id!==S.sesion) return false;
  const sc=scoreAll(), tot=sc.reduce((a,x)=>a+x.pts,0), max=sc.reduce((a,x)=>a+x.max,0), prev=s.pruebas[CARPETA]||{};
  s.pruebas[CARPETA]={nombre:TEST_NAME,estado:S.status,app:S.id,fin:S.finishedAt||now(),tot,max,pct:Math.round(tot/max*100),
    prompt:buildPrompt(sc),incid:prev.app===S.id?(prev.incid||""):""};
  return sesionGuardar(s);
}
/* Pantalla final con sesión: el resultado ya está en el menú; se limpia la prueba y se vuelve a él.
   Si la sesión no se pudo actualizar, los resultados se muestran aquí para no perderlos. */
function volverAlMenu(){
  if(!registrarEnSesion()){toast("No se pudo pasar el resultado al menú; se muestra aquí");S.phase="results";save();render();return;}
  clearStore();S=blank();location.href="../";
}
if(RESUMED&&S.phase==="done") registrarEnSesion();
if(!AL_MENU) render();
