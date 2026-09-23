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


async def mantener(pg, selector, ms):
    elemento = pg.locator(selector).first
    await elemento.scroll_into_view_if_needed()
    caja = await elemento.bounding_box()
    await pg.mouse.move(caja["x"] + 20, caja["y"] + 10)
    await pg.mouse.down()
    await pg.clock.run_for(ms)
    await pg.mouse.up()
    await pg.clock.run_for(200)


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
            # Reloj simulado: las pulsaciones largas y el avance automático se adelantan sin dormir.
            await ctx.clock.install()
            # Sin Google Fonts: el menú debe funcionar igual con la fuente del sistema y sin depender de internet.
            await ctx.route("https://fonts.googleapis.com/**", lambda r: r.abort())
            await ctx.route("https://fonts.gstatic.com/**", lambda r: r.abort())
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

            historial = "JSON.parse(localStorage.getItem('rgFormaB.v1.historial') || '[]')"

            # Botón visible "Salir": en todas las pantallas de la prueba; un toque corto solo avisa;
            # mantenido 3 s abre el menú del aplicador, que cancela y vuelve al menú de pruebas.
            await pg.goto(raiz + "vacia.html")
            await pg.evaluate("localStorage.clear()")
            await pg.goto(raiz + "razonamiento-forma-b/")
            await pg.fill("#f-nombre", "Eva Soto")
            await pg.click("[data-act=mode][data-v=ext]")
            await pg.click("[data-act=toWelcome]")
            comprobar(await pg.locator(".salir").count() == 1, "la bienvenida no tiene el botón Salir")
            await pg.click("[data-act=begin]")
            comprobar(await pg.locator(".salir").count() == 1, "la introducción de la parte no tiene el botón Salir")
            await pg.click("[data-act=startSeries]")
            caja = await pg.locator(".bar .salir").bounding_box()
            comprobar(caja and caja["height"] >= 56 and caja["width"] >= 56, f"el botón Salir de la barra mide menos de 56 px: {caja}")
            await mantener(pg, ".bar .salir", 300)
            comprobar(await pg.locator(".modal").count() == 0, "un toque corto en Salir abrió el menú")
            comprobar("mantén presionado 3 segundos" in await pg.inner_text("#toast"), "un toque corto en Salir no avisó cómo usarlo")
            await pg.click("[data-act=toReview]")
            comprobar(await pg.locator(".bar .salir").count() == 1, "la revisión de la parte no tiene el botón Salir")
            await mantener(pg, ".bar .salir", 3200)
            await pg.click(".modal >> text=Volver al menú de pruebas")
            await pg.click(".modal >> text=Sí, cancelar y volver")
            await pg.wait_for_url(raiz)
            await pg.wait_for_timeout(300)
            comprobar(pg.url == raiz and await pg.locator(".prueba").count() == len(carpetas), "Salir no volvió al menú de pruebas")
            comprobar(await pg.evaluate("localStorage.getItem('rgFormaB.v1') === null"), "al volver al menú quedó la aplicación en curso")
            h = await pg.evaluate(historial)
            comprobar(any(x["cand"]["nombre"] == "Eva Soto" and x["status"] == "cancelada" for x in h), "la aplicación cancelada con Salir no quedó en el historial")

            # Preparar para un candidato nuevo sin nada pendiente: no cambia nada.
            antes = len(h)
            await mantener(pg, "#preparar", 3200)
            comprobar("No hay aplicaciones pendientes" in await pg.inner_text("#toast"), "sin pendientes no avisó")
            comprobar(len(await pg.evaluate(historial)) == antes, "sin pendientes modificó el historial")

            # Aplicación real sin terminar con la hora límite vencida: se cancela, se archiva y se limpia.
            await pg.goto(raiz + "razonamiento-forma-b/")
            await pg.fill("#f-nombre", "Raúl Díaz")
            await pg.click("[data-act=mode][data-v=std]")
            await pg.click("[data-act=toWelcome]")
            await pg.click("[data-act=begin]")
            await pg.click("[data-act=startSeries]")
            await pg.click('[data-act=pick][data-ctx=real][data-v="3"]')
            await pg.clock.run_for(400)
            await pg.goto(raiz + "vacia.html")
            estado = await pg.evaluate("localStorage.getItem('rgFormaB.v1')")
            await pg.evaluate("localStorage.removeItem('rgFormaB.v1'); localStorage.removeItem('rgFormaB.v1.respaldo')")
            await pg.goto(raiz)
            await pg.evaluate("""e => {
                const o = JSON.parse(e); o.times.I.deadline = Date.now() - 60000;
                localStorage.setItem('rgFormaB.v1', '{dañado');
                localStorage.setItem('rgFormaB.v1.respaldo', JSON.stringify(o));
            }""", estado)
            await mantener(pg, "#preparar", 3200)
            texto = await pg.inner_text(".modal")
            comprobar("Raúl Díaz" in texto and "Sin terminar" in texto, f"la confirmación no describe la aplicación pendiente: {texto}")
            await pg.click(".modal >> text=Sí, preparar")
            await pg.wait_for_timeout(200)
            comprobar(await pg.evaluate("localStorage.getItem('rgFormaB.v1') === null && localStorage.getItem('rgFormaB.v1.respaldo') === null"), "preparar no limpió el estado en curso")
            h = await pg.evaluate(historial)
            raul = [x for x in h if x["cand"]["nombre"] == "Raúl Díaz"]
            comprobar(len(raul) == 1 and raul[0]["status"] == "cancelada" and raul[0]["phase"] == "done", "preparar no archivó la aplicación sin terminar como cancelada")
            if raul:
                t_i = raul[0]["times"]["I"]
                comprobar(t_i.get("end") == t_i.get("deadline") and t_i.get("timedOut") is True, "el reloj vencido no se cerró en la hora límite")
                comprobar(raul[0]["ans"]["I"][0] == 3, "se perdió la respuesta contestada")
            comprobar(pg.url == raiz, "preparar redirigió fuera del menú")

            # Aplicación terminada (ya archivada al terminar): se limpia sin duplicarla en el historial.
            await pg.evaluate("""() => {
                const h = JSON.parse(localStorage.getItem('rgFormaB.v1.historial'));
                const o = Object.assign({}, h[0], {id: 'Aterminada', status: 'terminada', phase: 'results', cand: {nombre: 'Sara Luna'}});
                h.unshift(o);
                localStorage.setItem('rgFormaB.v1.historial', JSON.stringify(h));
                localStorage.setItem('rgFormaB.v1', JSON.stringify(o));
            }""")
            antes = len(await pg.evaluate(historial))
            await mantener(pg, "#preparar", 3200)
            comprobar("Terminada" in await pg.inner_text(".modal"), "la confirmación no distingue la aplicación terminada")
            await pg.click(".modal >> text=Sí, preparar")
            await pg.wait_for_timeout(200)
            h = await pg.evaluate(historial)
            comprobar(len(h) == antes and await pg.evaluate("localStorage.getItem('rgFormaB.v1') === null"), "la aplicación terminada se duplicó o no se limpió")

            # Tras preparar, la prueba abre directo en la pantalla de captura.
            await pg.click('.prueba[href="razonamiento-forma-b/"]')
            await pg.wait_for_url(raiz + "razonamiento-forma-b/")
            comprobar(await pg.locator("#f-nombre").count() == 1, "tras preparar, la prueba no abrió en la pantalla de captura")
            guardadas = await pg.locator(".hist button").all_inner_texts()
            comprobar(any("Raúl Díaz" in g and "cancelada" in g for g in guardadas), f"la prueba no muestra en su historial lo archivado por el menú: {guardadas}")
            await pg.click(".hist button >> text=Raúl Díaz")
            comprobar(await pg.inner_text("h1") == "Raúl Díaz", "la prueba no abrió los resultados archivados por el menú")

            # Fuera de Pages (archivo local o artefacto) no se ofrece volver al menú.
            await pg.goto((REPO / "pruebas" / "razonamiento-forma-b" / "src" / "prueba.html").as_uri())
            await pg.evaluate("localStorage.clear()")
            await pg.reload()
            comprobar(await pg.locator("text=Cambiar de prueba").count() == 0, "ofrece volver al menú fuera del sitio publicado")
            await pg.fill("#f-nombre", "Local")
            await pg.click("[data-act=mode][data-v=std]")
            await pg.click("[data-act=toWelcome]")
            await pg.click("[data-act=begin]")
            await mantener(pg, ".pnum", 3200)
            comprobar(await pg.locator(".modal >> text=Volver al menú de pruebas").count() == 0, "el menú oculto ofrece volver al menú fuera del sitio publicado")
            await nav.close()
        servidor.shutdown()

    if errores:
        fallas.append("errores de JavaScript: " + "; ".join(errores))
    if fallas:
        print("FALLAS:\n- " + "\n- ".join(fallas))
        sys.exit(1)
    print(f"OK: menú con {len(carpetas)} prueba(s), ida y vuelta, reanudación, botón Salir y preparar candidato nuevo")


asyncio.run(main())
