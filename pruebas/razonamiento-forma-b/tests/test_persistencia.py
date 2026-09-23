"""Recarga, respaldo, bloqueo con dos pestañas, historial y cancelación."""
import asyncio
import sys
from playwright.async_api import async_playwright
from comun import URL, iniciar, terminar_parte, mantener, reloj, esperar


async def main():
    fallas, errores = [], []

    def comprobar(cond, texto):
        if not cond:
            fallas.append(texto)

    async with async_playwright() as p:
        nav = await p.chromium.launch()
        ctx = await nav.new_context(viewport={"width": 390, "height": 844}, has_touch=True)
        pg = await ctx.new_page()
        pg.on("pageerror", lambda e: errores.append(str(e)))
        await reloj(pg)
        await iniciar(pg, "Ana Ruiz")
        await pg.click("[data-act=startSeries]")
        for v in (3, 1, 2):
            await pg.click(f'[data-act=pick][data-ctx=real][data-v="{v}"]')
            await esperar(pg, 400)
        await pg.reload()
        await pg.wait_for_timeout(300)
        comprobar(await pg.inner_text(".qnum") == "Pregunta 4 de 16", "no reanudó en la pregunta 4")
        await pg.click("[data-act=prev]")
        comprobar(await pg.get_attribute('[data-act=pick][data-v="2"]', "aria-pressed") == "true", "se perdió la respuesta 3")

        await pg.evaluate("localStorage.setItem('rgFormaB.v1','{dañado')")
        await pg.reload()
        await pg.wait_for_timeout(300)
        comprobar(await pg.inner_text(".qnum") == "Pregunta 3 de 16", "el respaldo no recuperó el avance")

        pg2 = await ctx.new_page()
        await pg2.goto(URL)
        await pg2.wait_for_timeout(400)
        comprobar(await pg.locator("text=Esta ventana se bloqueó").count() == 1, "la pestaña vieja no se bloqueó")
        await pg.close()
        pg = pg2

        for _ in range(10):
            if await pg.locator("[data-act=startSeries]").count():
                await pg.click("[data-act=startSeries]")
            await pg.click("[data-act=toReview]")
            await terminar_parte(pg)
        await pg.reload()
        await pg.wait_for_timeout(300)
        comprobar(await pg.inner_text("h1") == "Terminaste la prueba", "tras terminar, la recarga no volvió a la pantalla final")
        await mantener(pg, "#hold", 1700)
        comprobar(await pg.inner_text("h1") == "Ana Ruiz", "no abrió resultados")
        await pg.click("[data-act=newTest]")
        await pg.locator(".modal .btn").last.click()
        comprobar(await pg.locator(".hist button").count() == 1, "la aplicación terminada no quedó en el historial")

        await pg.fill("#f-nombre", "Luis Mora")
        await pg.click("[data-act=mode][data-v=std]")
        await pg.click("[data-act=toWelcome]")
        await pg.click("[data-act=begin]")
        await pg.click("[data-act=startSeries]")
        await mantener(pg, ".part", 3200)
        await pg.locator(".modal .btn").last.click()
        await pg.locator(".modal .btn").last.click()
        await pg.wait_for_timeout(150)
        estados = await pg.locator(".hist button").all_inner_texts()
        comprobar(any("cancelada" in e for e in estados), "la cancelación no quedó en el historial")
        await nav.close()
    fallas += [f"error JS: {e}" for e in errores]
    print("\n".join(fallas) if fallas else "OK: recarga, respaldo, pestañas, historial y cancelación")
    sys.exit(1 if fallas else 0)


asyncio.run(main())
