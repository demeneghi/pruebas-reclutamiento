"""Flujo del menú de pruebas con sesión del candidato: arma el sitio como el workflow de Pages y lo sirve en local."""
import asyncio
import json
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

    clave = json.loads((REPO / "pruebas" / "razonamiento-forma-b" / "datos" / "clave.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        carpetas = armar_sitio(Path(tmp))
        # Página vacía del mismo origen: permite tocar localStorage sin que la prueba lo reescriba al salir.
        (Path(tmp) / "vacia.html").write_text("<!DOCTYPE html><title>vacía</title>", encoding="utf-8")
        servidor = servir(tmp)
        raiz = f"http://127.0.0.1:{servidor.server_address[1]}/"
        prueba = raiz + "razonamiento-forma-b/"
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
            visible = lambda sel: pg.locator(sel).is_visible()
            leer = lambda k: pg.evaluate(f"JSON.parse(localStorage.getItem('{k}') || 'null')")

            async def limpiar():
                await pg.goto(raiz + "vacia.html")
                await pg.evaluate("localStorage.clear()")

            async def capturar(nombre, puesto="Cortador", modo="ext"):
                await pg.fill("#f-nombre", nombre)
                await pg.fill("#f-edad", "34")
                await pg.select_option("#f-esc", "Secundaria")
                await pg.fill("#f-puesto", puesto)
                await pg.click(f"[data-act=mode][data-v={modo}]")
                await pg.fill("#f-aplic", "Luis")
                await pg.click("[data-act=continuar]")

            async def terminar_prueba(comenzar=True):
                if comenzar:
                    await pg.click("[data-act=begin]")
                for sid in clave:
                    await pg.click("[data-act=startSeries]")
                    if sid == "I":
                        await pg.click(f'[data-act=pick][data-ctx=real][data-v="{clave["I"][0]}"]')
                        await pg.clock.run_for(400)
                    await pg.click("[data-act=toReview]")
                    await pg.click("[data-act=endSeries]")
                    await pg.locator(".modal .btn").last.click()

            # Estructura: sin candidato capturado se ve la captura; las tarjetas son exactamente las pruebas publicadas.
            await limpiar()
            await pg.goto(raiz)
            comprobar(await visible("#v-captura") and not await visible("#candidato"), "sin candidato no se muestra la captura")
            enlaces = await pg.eval_on_selector_all(".prueba", "els => els.map(e => e.getAttribute('href'))")
            comprobar(sorted(enlaces) == sorted(c + "/" for c in carpetas), f"el menú no lista exactamente las pruebas publicadas: {enlaces} frente a {carpetas}")
            comprobar(await pg.eval_on_selector("body", "b => b.scrollWidth <= innerWidth"), "la captura tiene desplazamiento horizontal")
            alturas = await pg.eval_on_selector_all("#v-captura button", "els => els.map(e => e.getBoundingClientRect().height)")
            comprobar(all(h >= 56 for h in alturas), f"botones de la captura de menos de 56 px: {alturas}")

            # Una prueba abierta sin candidato capturado manda al menú.
            await pg.goto(prueba)
            await pg.wait_for_url(raiz)
            comprobar(await visible("#v-captura"), "la prueba sin candidato no mandó a la captura")

            # Validación y captura.
            await pg.click("[data-act=continuar]")
            comprobar("nombre del candidato" in await pg.inner_text("#toast"), "sin nombre no avisó")
            await pg.fill("#f-nombre", "Eva Soto")
            await pg.click("[data-act=continuar]")
            comprobar("tipo de puesto" in await pg.inner_text("#toast"), "sin tipo de puesto no avisó")
            await capturar("Eva Soto", "Cortadora")
            comprobar(await visible("#v-pruebas") and await pg.inner_text("#cand-nombre") == "Eva Soto", "tras la captura no se ven las pruebas con el nombre del candidato")
            await pg.click("[data-act=editar]")
            comprobar(await pg.input_value("#f-puesto") == "Cortadora", "editar no conservó los datos")
            await pg.fill("#f-puesto", "Empacadora")
            await pg.click("[data-act=continuar]")
            comprobar("Empacadora" in await pg.inner_text("#candidato"), "editar no actualizó la banda del candidato")
            alturas = await pg.eval_on_selector_all(".abrir, #v-pruebas .hold", "els => els.map(e => e.getBoundingClientRect().height)")
            comprobar(all(h >= 56 for h in alturas), f"botones del menú de menos de 56 px: {alturas}")

            # La prueba toma al candidato de la sesión y empieza en la bienvenida, sin pantalla de captura propia.
            await pg.click('.prueba[href="razonamiento-forma-b/"]')
            await pg.wait_for_url(prueba)
            comprobar(await pg.inner_text("h1") == "Hola, Eva" and await pg.locator("#f-nombre").count() == 0, "la prueba no empezó en la bienvenida con el candidato de la sesión")
            comprobar(await pg.locator(".salir").count() == 1, "la bienvenida no tiene el botón Salir")
            await pg.click("[data-act=begin]")
            comprobar(await pg.locator(".salir").count() == 1, "la introducción de la parte no tiene el botón Salir")
            await pg.click("[data-act=startSeries]")
            caja = await pg.locator(".bar .salir").bounding_box()
            comprobar(caja and caja["height"] >= 56 and caja["width"] >= 56, f"el botón Salir de la barra mide menos de 56 px: {caja}")
            await mantener(pg, ".bar .salir", 300)
            comprobar(await pg.locator(".modal").count() == 0, "un toque corto en Salir abrió el menú")
            comprobar("mantén presionado 3 segundos" in await pg.inner_text("#toast"), "un toque corto en Salir no avisó cómo usarlo")

            # Prueba en curso: la raíz la reabre sola, también con la copia principal dañada.
            await pg.goto(raiz)
            await pg.wait_for_url(prueba)
            comprobar(await pg.locator(".qnum").count() == 1, "la raíz no reanudó la prueba en curso")
            await pg.goto(raiz + "vacia.html")
            await pg.evaluate("localStorage.setItem('rgFormaB.v1','{dañado')")
            await pg.goto(raiz)
            await pg.wait_for_url(prueba)
            comprobar(await pg.locator(".qnum").count() == 1, "con la copia principal dañada no reanudó")

            # Salir mantenido 3 s: con sesión solo ofrece volver al menú; la prueba queda cancelada.
            await mantener(pg, ".bar .salir", 3200)
            comprobar(await pg.locator(".modal >> text=Cancelar aplicación").count() == 0, "con sesión el menú del aplicador ofrece cancelar sin volver al menú")
            await pg.click(".modal >> text=Volver al menú de pruebas")
            await pg.click(".modal >> text=Sí, cancelar y volver")
            await pg.wait_for_url(raiz)
            comprobar(await leer("rgFormaB.v1") is None, "al volver al menú quedó la aplicación en curso")
            comprobar("Cancelada" in await pg.inner_text(".prueba .estado"), "la tarjeta no quedó como cancelada")
            comprobar((await leer("arSesion.v1"))["pruebas"]["razonamiento-forma-b"]["estado"] == "cancelada", "la sesión no registró la cancelación")

            # "Atrás" a mitad de prueba: el menú queda en el historial y debe devolver a la prueba.
            await pg.click('.prueba[href="razonamiento-forma-b/"]')
            await pg.click(".modal >> text=Sí, aplicar de nuevo")
            await pg.wait_for_url(prueba)
            await pg.click("[data-act=begin]")
            await pg.go_back()
            await pg.wait_for_url(prueba)
            await pg.wait_for_timeout(300)
            comprobar(await pg.locator("[data-act=startSeries]").count() == 1, "con \"atrás\" no volvió a la prueba en curso")

            # Terminar la prueba: pantalla final sin resultados y pulsación del aplicador para volver al menú.
            await pg.goto(raiz + "vacia.html")
            await pg.goto(prueba)
            await terminar_prueba(comenzar=False)
            comprobar(await pg.inner_text("h1") == "Terminaste la prueba" and "volver al menú" in await pg.inner_text("#hold"), "la pantalla final no ofrece volver al menú")
            await mantener(pg, "#hold", 1700)
            await pg.wait_for_url(raiz)
            comprobar(await leer("rgFormaB.v1") is None, "al volver al menú quedó la prueba terminada en su estado")
            comprobar("Terminada" in await pg.inner_text(".prueba .estado"), "la tarjeta no quedó como terminada")
            hist = await leer("rgFormaB.v1.historial")
            comprobar(sum(1 for x in hist if x["cand"]["nombre"] == "Eva Soto") == 2, "la prueba no archivó la cancelada y la terminada en su historial")
            comprobar(not await visible("[data-act=editar]"), "con pruebas aplicadas todavía se pueden editar los datos")
            await pg.click('.prueba[href="razonamiento-forma-b/"]')
            comprobar(await pg.locator(".modal >> text=Esta prueba ya se aplicó").count() == 1 and pg.url == raiz, "una prueba terminada se pudo abrir de nuevo")
            await pg.locator(".modal .btn").last.click()
            await pg.goto(prueba)
            await pg.wait_for_url(raiz)

            # Resultados en el menú tras pulsación larga: incidencias por prueba y un solo prompt.
            await mantener(pg, "#ver-resultados", 1700)
            comprobar(await visible("#v-resultados") and await pg.inner_text("#cand-nombre") == "Eva Soto", "los resultados no muestran al candidato")
            await pg.fill("[data-incid]", "Ruido de tractor.")
            prompt = await pg.inner_text("#prompt")
            for texto in ("Candidato: Eva Soto", "Puesto al que aspira: Empacadora", "Estado de la aplicación: terminada",
                          "Incidencias anotadas por el aplicador: «Ruido de tractor.»", "## Respuestas reactivo por reactivo"):
                comprobar(texto in prompt, f"al prompt le falta: {texto}")
            comprobar("| ok |" in prompt, "el prompt no refleja la respuesta correcta")
            await pg.reload()
            await mantener(pg, "#ver-resultados", 1700)
            comprobar(await pg.input_value("[data-incid]") == "Ruido de tractor.", "las incidencias no se guardaron")
            await pg.click("[data-act=volver]")

            # Terminar con el candidato: queda en el historial de candidatos y el menú vuelve a la captura.
            await mantener(pg, "#terminar", 3200)
            await pg.click(".modal >> text=Sí, terminar")
            comprobar(await visible("#v-captura") and await pg.input_value("#f-nombre") == "" and not await visible("#candidato"), "terminar no dejó la captura lista")
            comprobar(await leer("arSesion.v1") is None, "terminar no limpió la sesión")
            await pg.click(".hist button >> text=Eva Soto")
            comprobar(await visible("#v-resultados") and await pg.locator("[data-incid]").count() == 0, "un candidato anterior no abre sus resultados de solo lectura")
            comprobar("«Ruido de tractor.»" in await pg.inner_text("#prompt"), "el candidato anterior perdió sus incidencias")
            await pg.click("[data-act=volver]")

            # Aplicación sobrante (en curso, con la hora límite vencida): al capturar al siguiente candidato
            # se archiva como cancelada con el reloj cerrado en su hora límite y se limpia.
            await capturar("Raúl Díaz", modo="std")
            await pg.click('.prueba[href="razonamiento-forma-b/"]')
            await pg.wait_for_url(prueba)
            await pg.click("[data-act=begin]")
            await pg.click("[data-act=startSeries]")
            await pg.click(f'[data-act=pick][data-ctx=real][data-v="{clave["I"][0]}"]')
            await pg.clock.run_for(400)
            await pg.goto(raiz + "vacia.html")
            estado = await pg.evaluate("localStorage.getItem('rgFormaB.v1')")
            await pg.evaluate("localStorage.clear()")
            await pg.goto(raiz)
            await pg.evaluate("""e => {
                const o = JSON.parse(e); o.times.I.deadline = Date.now() - 60000;
                localStorage.setItem('rgFormaB.v1', '{dañado');
                localStorage.setItem('rgFormaB.v1.respaldo', JSON.stringify(o));
            }""", estado)
            await capturar("Sara Luna")
            comprobar(await leer("rgFormaB.v1") is None and await leer("rgFormaB.v1.respaldo") is None, "la captura no limpió la aplicación sobrante")
            raul = [x for x in await leer("rgFormaB.v1.historial") if x["cand"]["nombre"] == "Raúl Díaz"]
            comprobar(len(raul) == 1 and raul[0]["status"] == "cancelada", "la aplicación sobrante no quedó archivada como cancelada")
            if raul:
                t_i = raul[0]["times"]["I"]
                comprobar(t_i.get("end") == t_i.get("deadline") and t_i.get("timedOut") is True, "el reloj vencido no se cerró en la hora límite")

            # Una aplicación terminada de otra sesión no aparece al siguiente candidato.
            await pg.goto(raiz + "vacia.html")
            await pg.evaluate("""() => {
                const h = JSON.parse(localStorage.getItem('rgFormaB.v1.historial'));
                const o = Object.assign({}, h[0], {id: 'Avieja', status: 'terminada', phase: 'done', sesion: 'Sotra', cand: {nombre: 'Otro'}});
                localStorage.setItem('rgFormaB.v1', JSON.stringify(o));
            }""")
            await pg.goto(prueba)
            comprobar(await pg.inner_text("h1") == "Hola, Sara", "una prueba terminada de otra sesión se mostró al siguiente candidato")

            # Fuera de Pages (archivo local o artefacto) la prueba conserva su captura propia y su cancelación.
            await pg.goto((REPO / "pruebas" / "razonamiento-forma-b" / "src" / "prueba.html").as_uri())
            await pg.evaluate("localStorage.clear()")
            await pg.reload()
            comprobar(await pg.locator("#f-nombre").count() == 1 and await pg.locator("text=Cambiar de prueba").count() == 0, "fuera de Pages la prueba no muestra su captura propia")
            await pg.fill("#f-nombre", "Local")
            await pg.click("[data-act=mode][data-v=std]")
            await pg.click("[data-act=toWelcome]")
            await pg.click("[data-act=begin]")
            await mantener(pg, ".salir", 3200)
            comprobar(await pg.locator(".modal >> text=Volver al menú de pruebas").count() == 0 and await pg.locator(".modal >> text=Cancelar aplicación").count() == 1, "fuera de Pages el menú del aplicador no es el de la prueba suelta")
            await nav.close()
        servidor.shutdown()

    if errores:
        fallas.append("errores de JavaScript: " + "; ".join(errores))
    if fallas:
        print("FALLAS:\n- " + "\n- ".join(fallas))
        sys.exit(1)
    print(f"OK: menú con {len(carpetas)} prueba(s): captura, sesión, reanudación, Salir, final, resultados, cierre e historial")


asyncio.run(main())
