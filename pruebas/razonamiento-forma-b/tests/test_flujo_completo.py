"""Contesta las 165 preguntas correctamente. Exige que cada pregunta avance y un total de 199/199."""
import asyncio
import sys
from playwright.async_api import async_playwright
from comun import CLAVE, SERIES, iniciar, terminar_parte, mantener


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
        await iniciar(pg, "Flujo completo")
        for sid in SERIES:
            await pg.click("[data-act=startSeries]")
            for i, k in enumerate(CLAVE[sid]):
                antes = await etiqueta(pg)
                if sid == "IV":
                    for x in k:
                        await pg.click(f'[data-act=toggle][data-ctx=real][data-v="{x}"]')
                    await pg.wait_for_timeout(650)
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
                    await pg.wait_for_timeout(400)
                if antes == await etiqueta(pg):
                    fallas.append(f"{sid}-{i + 1} no avanzó")
            await terminar_parte(pg)
        await mantener(pg, "#hold", 1700)
        prompt = await pg.inner_text("#prompt")
        await nav.close()
    total = [l for l in prompt.split("\n") if l.startswith("| Total | | 1")]
    if not total or "| 199 | 199 | 100 |" not in total[0]:
        fallas.append(f"total inesperado: {total}")
    fallas += [f"error JS: {e}" for e in errores]
    print("\n".join(fallas) if fallas else "OK: 165 reactivos, 199/199, sin errores")
    sys.exit(1 if fallas else 0)


asyncio.run(main())
