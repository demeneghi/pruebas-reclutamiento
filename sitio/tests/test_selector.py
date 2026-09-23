"""Menú de pruebas de la raíz: arma el sitio como el workflow de Pages y lo sirve en local."""
import asyncio
import functools
import http.server
import shutil
import sys
import tempfile
import threading
from pathlib import Path
from playwright.async_api import async_playwright

REPO = Path(__file__).resolve().parents[2]


def armar_sitio(destino):
    """Replica el paso "Armar sitio" de .github/workflows/pages.yml."""
    shutil.copy(REPO / "sitio" / "index.html", destino / "index.html")
    carpetas = []
    for app in sorted(REPO.glob("pruebas/*/src/prueba.html")):
        carpeta = app.parent.parent.name
        (destino / carpeta).mkdir()
        shutil.copy(app, destino / carpeta / "index.html")
        carpetas.append(carpeta)
    return carpetas


class Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def servir(raiz):
    manejador = functools.partial(Silencioso, directory=str(raiz))
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), manejador)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    return servidor


async def main():
    fallas, errores = [], []

    def comprobar(cond, texto):
        if not cond:
            fallas.append(texto)

    with tempfile.TemporaryDirectory() as tmp:
        carpetas = armar_sitio(Path(tmp))
        # Página vacía del mismo origen: permite tocar localStorage sin que la prueba lo reescriba al salir.
        (Path(tmp) / "vacia.html").write_text("<!DOCTYPE html><title>vacía</title>", encoding="utf-8")
        servidor = servir(tmp)
        raiz = f"http://127.0.0.1:{servidor.server_address[1]}/"
        async with async_playwright() as p:
            nav = await p.chromium.launch()
            ctx = await nav.new_context(viewport={"width": 390, "height": 844}, has_touch=True)
            pg = await ctx.new_page()
            pg.on("pageerror", lambda e: errores.append(str(e)))

            await pg.goto(raiz)
            enlaces = await pg.eval_on_selector_all(".prueba", "els => els.map(e => e.getAttribute('href'))")
            comprobar(sorted(enlaces) == sorted(c + "/" for c in carpetas),
                      f"el menú no lista exactamente las pruebas publicadas: {enlaces} frente a {carpetas}")
            comprobar(await pg.eval_on_selector("body", "b => b.scrollWidth <= innerWidth"), "el menú tiene desplazamiento horizontal")
            alturas = await pg.eval_on_selector_all(".abrir", "els => els.map(e => e.getBoundingClientRect().height)")
            comprobar(all(h >= 56 for h in alturas), f"botones de menos de 56 px: {alturas}")

            for carpeta in carpetas:
                await pg.goto(raiz)
                await pg.click(f'.prueba[href="{carpeta}/"]')
                await pg.wait_for_url(raiz + carpeta + "/")
                comprobar(await pg.locator("#f-nombre").count() == 1, f"{carpeta}: no abrió la pantalla del aplicador")
                await pg.click("text=Cambiar de prueba")
                await pg.wait_for_url(raiz)
                comprobar(await pg.locator(".prueba").count() == len(carpetas), f"{carpeta}: no volvió al menú")

            # Prueba en curso: la raíz la reabre sola y el candidato no ve el menú.
            await pg.goto(raiz + "razonamiento-forma-b/")
            await pg.evaluate("localStorage.clear()")
            await pg.reload()
            await pg.fill("#f-nombre", "Ana Ruiz")
            await pg.click("[data-act=mode][data-v=ext]")
            await pg.click("[data-act=toWelcome]")
            await pg.click("[data-act=begin]")
            await pg.goto(raiz)
            await pg.wait_for_url(raiz + "razonamiento-forma-b/")
            comprobar(await pg.locator("[data-act=startSeries]").count() == 1, "la raíz no reanudó la prueba en curso")

            # "Atrás" a mitad de prueba: el menú queda en el historial y debe devolver a la prueba.
            await pg.goto(raiz + "vacia.html")
            await pg.evaluate("localStorage.clear()")
            await pg.goto(raiz)
            await pg.click('.prueba[href="razonamiento-forma-b/"]')
            await pg.wait_for_url(raiz + "razonamiento-forma-b/")
            await pg.fill("#f-nombre", "Luis Mora")
            await pg.click("[data-act=mode][data-v=std]")
            await pg.click("[data-act=toWelcome]")
            await pg.click("[data-act=begin]")
            await pg.go_back()
            await pg.wait_for_url(raiz + "razonamiento-forma-b/")
            await pg.wait_for_timeout(300)
            comprobar(await pg.locator("[data-act=startSeries]").count() == 1, "con \"atrás\" no volvió a la prueba en curso")

            # Copia principal dañada: decide con el respaldo, como la prueba.
            await pg.goto(raiz + "vacia.html")
            await pg.evaluate("localStorage.setItem('rgFormaB.v1','{dañado')")
            await pg.goto(raiz)
            await pg.wait_for_url(raiz + "razonamiento-forma-b/")
            comprobar(await pg.locator("[data-act=startSeries]").count() == 1, "con la copia principal dañada no reanudó")

            # Prueba terminada: la raíz ya no redirige; el aplicador puede elegir otra.
            await pg.goto(raiz + "vacia.html")
            await pg.evaluate("""() => {
                for (const k of ['rgFormaB.v1', 'rgFormaB.v1.respaldo']) {
                    const o = JSON.parse(localStorage.getItem(k)); o.phase = 'done';
                    localStorage.setItem(k, JSON.stringify(o));
                }
            }""")
            await pg.goto(raiz)
            await pg.wait_for_timeout(300)
            comprobar(pg.url == raiz, "la raíz redirigió con una prueba ya terminada")
            comprobar(await pg.locator(".prueba.activa").count() == 0, "marcó como en curso una prueba terminada")

            # Fuera de Pages (archivo local o artefacto) no se ofrece volver al menú.
            await pg.goto((REPO / "pruebas" / "razonamiento-forma-b" / "src" / "prueba.html").as_uri())
            await pg.evaluate("localStorage.clear()")
            await pg.reload()
            comprobar(await pg.locator("text=Cambiar de prueba").count() == 0, "ofrece volver al menú fuera del sitio publicado")
            await nav.close()
        servidor.shutdown()

    if errores:
        fallas.append("errores de JavaScript: " + "; ".join(errores))
    if fallas:
        print("FALLAS:\n- " + "\n- ".join(fallas))
        sys.exit(1)
    print(f"OK: menú con {len(carpetas)} prueba(s), ida y vuelta, reanudación y prueba terminada")


asyncio.run(main())
