"""Utilidades compartidas por las pruebas de extremo a extremo."""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HTML = RAIZ / "src" / "prueba.html"
URL = HTML.as_uri()
CLAVE = json.loads((RAIZ / "datos" / "clave.json").read_text(encoding="utf-8"))
SERIES = ["A", "B", "C", "D", "E"]


async def reloj(pg):
    """Reloj simulado para toda la página: las esperas de la aplicación (avance automático,
    pulsaciones largas, tiempos por reactivo) se adelantan con esperar() en lugar de dormir.
    Debe instalarse antes de la primera navegación."""
    await pg.context.clock.install()


async def esperar(pg, ms):
    """Adelanta el reloj simulado ms milisegundos y dispara los temporizadores vencidos."""
    await pg.clock.run_for(ms)


async def iniciar(pg, nombre="Prueba", modo="ext"):
    await pg.goto(URL)
    await pg.evaluate("localStorage.clear()")
    await pg.reload()
    await pg.fill("#f-nombre", nombre)
    await pg.click(f"[data-act=mode][data-v={modo}]")
    await pg.click("[data-act=toWelcome]")
    await pg.click("[data-act=begin]")


async def terminar_parte(pg):
    await pg.click("[data-act=endSeries]")
    await pg.locator(".modal .btn").last.click()


async def mantener(pg, selector, ms):
    caja = await (await pg.query_selector(selector)).bounding_box()
    await pg.mouse.move(caja["x"] + 20, caja["y"] + 10)
    await pg.mouse.down()
    await esperar(pg, ms)
    await pg.mouse.up()
    await esperar(pg, 150)
