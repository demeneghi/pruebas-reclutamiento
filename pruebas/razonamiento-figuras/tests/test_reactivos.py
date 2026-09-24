"""Los datos están al día con el generador y cada opción se distingue a simple vista de las demás.

- datos/*.json es exactamente lo que produce fuentes/generar_reactivos.py (nadie los editó a mano).
- Cada opción de cada reactivo y de cada ejemplo se dibuja a 100 x 100 px. En dos opciones del mismo reactivo,
  los píxeles distintos deben ser al menos MIN_DIF de los píxeles con tinta de cualquiera de las dos (la unión).
  Así ningún distractor duplica la respuesta ni otro distractor, y una diferencia chica no se pierde entre
  mucha tinta (por ejemplo, una figura pequeña encima de un rayado).
- Serie A: ningún distractor puede ser la respuesta corrida (la misma textura desplazada). Se compara cada
  distractor con la respuesta desplazada hasta 30 px en cada eje (medio periodo de la textura más amplia),
  solo en la parte que se traslapa, y la menor diferencia debe llegar a MIN_DIF_CORRIDA. El desplazamiento es
  de 1 px; para que sea rápido, en cada desplazamiento se compara un píxel de cada cuatro (uno por cuadro de 2 x 2). Un distractor así solo se
  distingue por cómo quedan cortadas las figuras en el borde: sería una segunda respuesta defendible.
"""
import asyncio
import importlib.util
import json
import sys
from playwright.async_api import async_playwright
from comun import RAIZ, CLAVE

# Calibrado revisando a ojo los pares más parecidos: un punto de más, un círculo frente a un pentágono chico
# o un relleno distinto en una figura chica quedan entre 9 y 15 %; un duplicado da 0 %.
MIN_DIF = 0.08
DESPLAZAMIENTO = 30
# Calibrado con la versión anterior de A5 y A6: la textura corrida medio espacio dio 2 %; los distractores
# de verdad distintos, 22 % o más.
MIN_DIF_CORRIDA = 0.12


def cargar(nombre):
    return json.loads((RAIZ / "datos" / nombre).read_text(encoding="utf-8"))


async def main():
    fallas = []
    spec = importlib.util.spec_from_file_location("generar_reactivos", RAIZ / "fuentes" / "generar_reactivos.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    reactivos, clave, desc, ejemplos = gen.generar()
    for nombre, datos in (("reactivos.json", reactivos), ("clave.json", clave), ("descripciones.json", desc), ("ejemplos.json", ejemplos)):
        if json.loads(json.dumps(datos, ensure_ascii=False)) != cargar(nombre):
            fallas.append(f"datos/{nombre} no coincide con el generador; corre fuentes/generar_reactivos.py")

    # Se revisa lo que llega a la aplicación: los datos, no la salida del generador.
    grupos = [(f"{s}-{i + 1:02d}", it["opciones"], CLAVE[s][i] if s == "A" else -1) for s, lista in cargar("reactivos.json").items() for i, it in enumerate(lista)]
    grupos += [(f"ejemplo {s}", it["opciones"], it["key"] if s == "A" else -1) for s, it in cargar("ejemplos.json").items()]
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        pg = await nav.new_page()
        await pg.set_content("<canvas id=c width=100 height=100></canvas>")
        difs = await pg.evaluate("""async ([grupos, D]) => {
            const c = document.getElementById('c'), g = c.getContext('2d', {willReadFrequently: true});
            async function mascara(svg) {
                const img = new Image();
                img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">' + svg + '</svg>');
                await img.decode();
                g.fillStyle = '#fff'; g.fillRect(0, 0, 100, 100); g.drawImage(img, 0, 0);
                const d = g.getImageData(0, 0, 100, 100).data, m = new Uint8Array(10000);
                for (let i = 0; i < 10000; i++) m[i] = d[i * 4] < 128 ? 1 : 0;
                return m;
            }
            const out = [];
            /* Menor diferencia entre a y b corrida (dx, dy), contando solo la parte que se traslapa. */
            function corrida(a, b) {
                let min = 1;
                for (let dy = -D; dy <= D; dy++) for (let dx = -D; dx <= D; dx++) {
                    let n = 0, u = 0;
                    for (let y = Math.max(0, dy); y < Math.min(100, 100 + dy); y += 2) for (let x = Math.max(0, dx); x < Math.min(100, 100 + dx); x += 2) {
                        const p = a[y * 100 + x], q = b[(y - dy) * 100 + x - dx];
                        n += p !== q; u += p | q;
                    }
                    if (u) min = Math.min(min, n / u);
                }
                return min;
            }
            for (const [nombre, ops, k] of grupos) {
                const ms = [];
                for (const o of ops) ms.push(await mascara(o));
                let min = 1, par = null;
                for (let a = 0; a < ms.length; a++) for (let b = a + 1; b < ms.length; b++) {
                    let n = 0, u = 0; for (let i = 0; i < 10000; i++) { n += ms[a][i] !== ms[b][i]; u += ms[a][i] | ms[b][i]; }
                    const r = n / Math.max(1, u);
                    if (r < min) { min = r; par = [a + 1, b + 1]; }
                }
                let minC = 1, parC = null;
                if (k >= 0) for (let j = 0; j < ms.length; j++) if (j !== k) {
                    const r = corrida(ms[j], ms[k]);
                    if (r < minC) { minC = r; parC = j + 1; }
                }
                out.push([nombre, min, par, minC, parC, k + 1]);
            }
            return out;
        }""", [grupos, DESPLAZAMIENTO])
        await nav.close()
    for nombre, minimo, par, min_c, op_c, correcta in difs:
        if minimo < MIN_DIF:
            fallas.append(f"{nombre}: las opciones {par[0]} y {par[1]} casi no se distinguen ({minimo:.0%} de la tinta es distinta)")
        if min_c < MIN_DIF_CORRIDA:
            fallas.append(f"{nombre}: la opción {op_c} es la respuesta ({correcta}) corrida unos píxeles ({min_c:.0%} de la tinta distinta al alinearlas)")
    peor = min(difs, key=lambda x: x[1])
    peor_c = min(difs, key=lambda x: x[3])
    print("\n".join(fallas) if fallas else f"OK: datos al día con el generador; {len(difs)} reactivos y ejemplos con opciones distinguibles (mínimo {peor[1]:.0%} de la tinta distinta, en {peor[0]}); en la serie A ningún distractor es la respuesta corrida (mínimo {peor_c[3]:.0%}, en {peor_c[0]})")
    sys.exit(1 if fallas else 0)


asyncio.run(main())
