"""Los datos están al día con el generador y cada opción se distingue a simple vista de las demás.

- datos/*.json es exactamente lo que produce fuentes/generar_reactivos.py (nadie los editó a mano).
- Cada opción de cada reactivo y de cada ejemplo se dibuja a 100 x 100 px. En dos opciones del mismo reactivo,
  los píxeles distintos deben ser al menos MIN_DIF de los píxeles con tinta de cualquiera de las dos (la unión).
  Así ningún distractor duplica la respuesta ni otro distractor, y una diferencia chica no se pierde entre
  mucha tinta (por ejemplo, una figura pequeña encima de un rayado).
"""
import asyncio
import importlib.util
import json
import sys
from playwright.async_api import async_playwright
from comun import RAIZ

# Calibrado revisando a ojo los pares más parecidos: un punto de más, un círculo frente a un pentágono chico
# o un relleno distinto en una figura chica quedan entre 9 y 15 %; un duplicado da 0 %.
MIN_DIF = 0.08


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

    grupos = [(f"{s}-{i + 1:02d}", it["opciones"]) for s, lista in reactivos.items() for i, it in enumerate(lista)]
    grupos += [(f"ejemplo {s}", it["opciones"]) for s, it in ejemplos.items()]
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        pg = await nav.new_page()
        await pg.set_content("<canvas id=c width=100 height=100></canvas>")
        difs = await pg.evaluate("""async grupos => {
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
            for (const [nombre, ops] of grupos) {
                const ms = [];
                for (const o of ops) ms.push(await mascara(o));
                let min = 1, par = null;
                for (let a = 0; a < ms.length; a++) for (let b = a + 1; b < ms.length; b++) {
                    let n = 0, u = 0; for (let i = 0; i < 10000; i++) { n += ms[a][i] !== ms[b][i]; u += ms[a][i] | ms[b][i]; }
                    const r = n / Math.max(1, u);
                    if (r < min) { min = r; par = [a + 1, b + 1]; }
                }
                out.push([nombre, min, par]);
            }
            return out;
        }""", grupos)
        await nav.close()
    for nombre, minimo, par in difs:
        if minimo < MIN_DIF:
            fallas.append(f"{nombre}: las opciones {par[0]} y {par[1]} casi no se distinguen ({minimo:.0%} de la tinta es distinta)")
    peor = min(difs, key=lambda x: x[1])
    print("\n".join(fallas) if fallas else f"OK: datos al día con el generador; {len(difs)} reactivos y ejemplos con opciones distinguibles (mínimo {peor[1]:.0%} de la tinta distinta, en {peor[0]})")
    sys.exit(1 if fallas else 0)


asyncio.run(main())
