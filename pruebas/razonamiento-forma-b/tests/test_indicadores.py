"""Registro por reactivo, condiciones de la aplicación, incidencias y restricción de edad en el prompt."""
import asyncio
import re
import sys
from playwright.async_api import async_playwright
from comun import CLAVE, URL, terminar_parte, mantener, reloj, esperar


def linea(prompt, prefijo):
    return next((l for l in prompt.split("\n") if l.startswith(prefijo)), "")


async def main():
    fallas, errores = [], []

    def comprobar(cond, texto):
        if not cond:
            fallas.append(texto)

    async with async_playwright() as p:
        nav = await p.chromium.launch()
        pg = await nav.new_page(viewport={"width": 390, "height": 844}, has_touch=True)
        pg.on("pageerror", lambda e: errores.append(str(e)))
        await reloj(pg)
        await pg.goto(URL)
        await pg.evaluate("localStorage.clear()")
        await pg.reload()
        await pg.fill("#f-nombre", "Rosa Díaz")
        await pg.fill("#f-edad", "47")
        await pg.fill("#f-anos", "30")
        await pg.select_option("#f-disp", "Casi nunca")
        await pg.click("[data-act=mode][data-v=ext]")
        await pg.click("[data-act=toWelcome]")
        await pg.click("[data-act=begin]")
        await pg.click("[data-act=startSeries]")

        k = CLAVE["I"]
        # I-01: respuesta rápida errónea, luego corregida.
        await pg.click(f'[data-act=pick][data-ctx=real][data-v="{(k[0] + 1) % 4}"]')
        await esperar(pg, 400)
        await pg.click("[data-act=prev]")
        await pg.click(f'[data-act=pick][data-ctx=real][data-v="{k[0]}"]')
        await esperar(pg, 400)
        # I-02: unos 3 s en pantalla con una recarga en medio; el tiempo previo se conserva.
        await esperar(pg, 1500)
        await pg.reload()
        await esperar(pg, 1500)
        await pg.click(f'[data-act=pick][data-ctx=real][data-v="{k[1]}"]')
        await esperar(pg, 400)
        # I-03: vista y dejada en blanco; I-04 en adelante, no vistas.
        await pg.click("[data-act=toReview]")
        await terminar_parte(pg)
        for _ in range(9):
            await pg.click("[data-act=startSeries]")
            await pg.click("[data-act=toReview]")
            await terminar_parte(pg)
        await mantener(pg, "#hold", 1700)
        await pg.fill("#f-incid", "Sonó su teléfono durante la parte 5.")
        prompt = await pg.inner_text("#prompt")

        comprobar("Uso de teléfono o tablet, según el aplicador: casi nunca" in prompt, "falta el uso de teléfono o tablet")
        comprobar("Años desde que dejó la escuela: 30" in prompt, "faltan los años desde que dejó la escuela")
        comprobar("Incidencias anotadas por el aplicador: «Sonó su teléfono durante la parte 5.»" in prompt, "las incidencias no llegaron al prompt")
        comprobar("No uses la edad para ajustar el puntaje" in prompt, "falta la restricción de edad")
        l1 = linea(prompt, "I-01 |")
        comprobar(" | ok | " in l1 and " | 1 (primera: " in l1, f"I-01 no registró el cambio: {l1}")
        t1 = re.search(r"\| ([\d.]+) s \| 1 \(", l1)
        comprobar(t1 and float(t1.group(1)) < 2, f"I-01 no quedó como respuesta rápida: {l1}")
        t2 = re.search(r"\| ([\d.]+) s \| 0$", linea(prompt, "I-02 |"))
        comprobar(t2 and 2.5 <= float(t2.group(1)) < 10, f"I-02 perdió el tiempo previo a la recarga: {linea(prompt, 'I-02 |')}")
        comprobar(linea(prompt, "I-03 |").endswith("| omitida | vista, sin respuesta | 0"), "I-03 no quedó como vista sin respuesta")
        comprobar(linea(prompt, "I-04 |").endswith("| omitida | no vista | 0"), "I-04 no quedó como no vista")
        fila = linea(prompt.split("## Indicadores de proceso")[1], "| I | Información |").split(" | ")
        # Serie, factor, mediana, rápidas, rápidas erróneas, error a acierto, acierto a error, otros, om. vistas, om. no vistas, precisión, % límite
        comprobar(fila[3:11] == ["1", "1", "1", "0", "0", "1", "13", "100"], f"indicadores de la serie I inesperados: {fila}")

        # Las incidencias se guardan y sobreviven a la recarga.
        await esperar(pg, 600)
        await pg.reload()
        await mantener(pg, "#hold", 1700)
        comprobar(await pg.input_value("#f-incid") == "Sonó su teléfono durante la parte 5.", "las incidencias no se guardaron")

        # Aplicación de una versión anterior, sin registro por reactivo.
        await pg.evaluate("delete S.log; render()")
        viejo = await pg.inner_text("#prompt")
        comprobar("no registró tiempos por reactivo" in viejo, "sin registro, el prompt no lo advierte")
        comprobar(linea(viejo, "I-01 |").endswith("| sin registro | sin registro"), "sin registro, el reactivo no lo indica")
        await nav.close()
    fallas += [f"error JS: {e}" for e in errores]
    print("\n".join(fallas) if fallas else "OK: tiempos por reactivo, cambios, omisiones, condiciones e incidencias")
    sys.exit(1 if fallas else 0)


asyncio.run(main())
