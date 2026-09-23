"""Contesta los 60 reactivos correctamente. Exige que cada pregunta avance, un total de 60/60, tiempo de primera
respuesta en cada reactivo, la regla de cada reactivo en el prompt, opciones de al menos 56 px y sin desplazamiento horizontal."""
import asyncio
import re
import sys
from playwright.async_api import async_playwright
from comun import CLAVE, SERIES, iniciar, terminar_parte, mantener, reloj, esperar


async def etiqueta(pg):
    return await pg.inner_text(".qnum") if await pg.locator(".qnum").count() else await pg.inner_text("h1")


async def main():
    fallas, errores = [], []
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        pg = await nav.new_page(viewport={"width": 390, "height": 844}, has_touch=True)
        pg.on("pageerror", lambda e: errores.append(str(e)))
        await reloj(pg)
        await iniciar(pg, "Flujo completo")
        for sid in SERIES:
            # El ejemplo de la serie: la opción correcta queda marcada en verde.
            await pg.click('[data-act=pick][data-ctx=ex][data-v="0"]')
            if await pg.locator("#exbox .opt.is-right").count() != 1:
                fallas.append(f"el ejemplo de la serie {sid} no marca la respuesta correcta")
            await pg.click("[data-act=startSeries]")
            for i, k in enumerate(CLAVE[sid]):
                antes = await etiqueta(pg)
                if i == 0:
                    alturas = await pg.eval_on_selector_all(".opt.fig", "els => els.map(e => e.getBoundingClientRect().height)")
                    if not alturas or min(alturas) < 56:
                        fallas.append(f"serie {sid}: opciones de menos de 56 px: {alturas}")
                    if not await pg.eval_on_selector("body", "b => b.scrollWidth <= innerWidth"):
                        fallas.append(f"serie {sid}: la pregunta tiene desplazamiento horizontal")
                await pg.click(f'[data-act=pick][data-ctx=real][data-v="{k}"]')
                await esperar(pg, 400)
                if antes == await etiqueta(pg):
                    fallas.append(f"{sid}-{i + 1} no avanzó")
            await terminar_parte(pg)
        await mantener(pg, "#hold", 1700)
        prompt = await pg.inner_text("#prompt")
        await nav.close()
    total = [l for l in prompt.split("\n") if l.startswith("| Total | | 6")]
    if not total or "| 60 | 60 | 100 |" not in total[0]:
        fallas.append(f"total inesperado: {total}")
    lineas = [l for l in prompt.split("\n") if re.match(r"^[A-E]-\d\d \| ", l)]
    con_tiempo = [l for l in lineas if re.search(r"\| ok \| \d+\.\d s \| 0$", l)]
    if len(lineas) != 60 or len(con_tiempo) != 60:
        fallas.append(f"reactivos con primera respuesta registrada y sin cambios: {len(con_tiempo)} de {len(lineas)}")
    if any(" | regla: " not in l or " | opción " not in l for l in lineas):
        fallas.append("hay reactivos sin regla o sin opción descrita en el prompt")
    fallas += [f"error JS: {e}" for e in errores]
    print("\n".join(fallas) if fallas else "OK: 60 reactivos, 60/60, sin errores")
    sys.exit(1 if fallas else 0)


asyncio.run(main())
