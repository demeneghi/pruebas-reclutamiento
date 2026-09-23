"""Utilidades compartidas por las pruebas de extremo a extremo."""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HTML = RAIZ / "src" / "prueba.html"
URL = HTML.as_uri()
CLAVE = json.loads((RAIZ / "datos" / "clave.json").read_text(encoding="utf-8"))
SERIES = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


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
    await pg.wait_for_timeout(ms)
    await pg.mouse.up()
    await pg.wait_for_timeout(150)
