"""Contesta las 165 preguntas correctamente. Exige que cada pregunta avance, un total de 199/199 y tiempo de primera respuesta en cada reactivo."""
import asyncio
import re
import sys
from playwright.async_api import async_playwright
from comun import CLAVE, SERIES, iniciar, terminar_parte, mantener, reloj, esperar


def cifra(x):
    s = str(x)
    return s[:-2] if s.endswith(".0") else s


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
        await pg.evaluate("document.fullscreenElement && document.exitFullscreen()")
        await pg.wait_for_timeout(300)
        if not await pg.locator("#fsbtn").is_visible():
            fallas.append("sin botón de pantalla completa al salir de ella")
        else:
            await pg.click("#fsbtn")
            await pg.wait_for_timeout(300)
            if await pg.locator("#fsbtn").is_visible() or not await pg.evaluate("!!document.fullscreenElement"):
                fallas.append("el botón no activó la pantalla completa")
        for sid in SERIES:
            await pg.click("[data-act=startSeries]")
            for i, k in enumerate(CLAVE[sid]):
                antes = await etiqueta(pg)
                if sid == "IV":
                    for x in k:
                        await pg.click(f'[data-act=toggle][data-ctx=real][data-v="{x}"]')
                    await esperar(pg, 650)
                elif sid == "V":
                    for c in cifra(k):
                        await pg.click(f'[data-act=key][data-ctx=real][data-v="{c}"]')
                    await pg.click('[data-act=key][data-ctx=real][data-v="ok"]')
                elif sid == "X":
                    for j in (0, 1):
                        for c in cifra(k[j]):
                            await pg.click(f'[data-act=key][data-ctx=real][data-v="{c}"]')
                        await pg.click('[data-act=key][data-ctx=real][data-v="ok"]')
                else:
                    await pg.click(f'[data-act=pick][data-ctx=real][data-v="{k}"]')
                    await esperar(pg, 400)
                if antes == await etiqueta(pg):
                    fallas.append(f"{sid}-{i + 1} no avanzó")
            await terminar_parte(pg)
        await mantener(pg, "#hold", 1700)
        prompt = await pg.inner_text("#prompt")
        await nav.close()
    total = [l for l in prompt.split("\n") if l.startswith("| Total | | 1")]
    if not total or "| 199 | 199 | 100 |" not in total[0]:
        fallas.append(f"total inesperado: {total}")
    lineas = [l for l in prompt.split("\n") if re.match(r"^[IVX]+-\d\d \| ", l)]
    con_tiempo = [l for l in lineas if re.search(r"\| ok \| \d+\.\d s \| 0$", l)]
    if len(lineas) != 165 or len(con_tiempo) != 165:
        fallas.append(f"reactivos con primera respuesta registrada y sin cambios: {len(con_tiempo)} de {len(lineas)}")
    if "## Indicadores de proceso" not in prompt:
        fallas.append("falta la sección de indicadores de proceso")
    fallas += [f"error JS: {e}" for e in errores]
    print("\n".join(fallas) if fallas else "OK: 165 reactivos, 199/199, sin errores")
    sys.exit(1 if fallas else 0)


asyncio.run(main())
