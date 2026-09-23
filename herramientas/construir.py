"""Arma pruebas/<prueba>/src/prueba.html a partir del motor común y de la carpeta de cada prueba.

Piezas, en el orden en que quedan dentro del HTML:
- motor/plantilla.html: esqueleto de la página.
- motor/fuentes.css y motor/motor.css: estilos comunes.
- pruebas/<prueba>/src/config.js: lo propio de la prueba (nombre, claves, series, textos del prompt).
- marca/logo-amador-russell.svg: logotipo animado (constante LOGO).
- pruebas/<prueba>/datos/reactivos.json y clave.json: reactivos (ITEMS) y clave ofuscada (KEY).
- Opcionales: datos/ejemplos.json (EJEMPLOS, ejemplos de práctica por serie cuando no caben en config.js)
  y datos/descripciones.json (DESC, regla y opciones en texto para el prompt, ofuscadas como la clave).
- motor/sesion.js: sesión del candidato compartida con el menú de pruebas.
- motor/motor.js: persistencia, flujo, calificación, prompt y eventos.

También copia motor/sesion.js en la región marcada de sitio/index.html (el menú de pruebas).

Uso:
    python herramientas/construir.py              # regenera todas las pruebas
    python herramientas/construir.py --verificar  # falla si algún archivo generado no está al día
"""
import base64
import html
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MOTOR = RAIZ / "motor"
MENU = RAIZ / "sitio" / "index.html"
REGION = re.compile(r"(/\* ==== Inicio de motor/sesion\.js[^\n]*\n)(.*?)(/\* ==== Fin de motor/sesion\.js ==== \*/)", re.S)
LOGO = RAIZ / "marca" / "logo-amador-russell.svg"


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


def constante_texto(config, nombre):
    m = re.search(r'^const ' + nombre + r' = ("(?:[^"\\]|\\.)*");$', config, re.M)
    if not m:
        raise SystemExit(f"config.js no define {nombre} como cadena en una sola línea")
    return json.loads(m.group(1))


def ofuscar(datos):
    return base64.b64encode(json.dumps(datos, ensure_ascii=False).encode("utf-8")).decode("ascii")


def construir(carpeta):
    config = leer(carpeta / "src" / "config.js")
    if constante_texto(config, "CARPETA") != carpeta.name:
        raise SystemExit(f"{carpeta.name}: CARPETA en config.js no coincide con el nombre de la carpeta")
    titulo = constante_texto(config, "TITULO")
    reactivos = json.loads(leer(carpeta / "datos" / "reactivos.json"))
    clave = json.loads(leer(carpeta / "datos" / "clave.json"))
    if list(reactivos) != list(clave) or any(len(reactivos[s]) != len(clave[s]) for s in reactivos):
        raise SystemExit(f"{carpeta.name}: reactivos.json y clave.json no tienen las mismas series y cantidades")
    logo = leer(LOGO).strip()
    if "'" in logo or "\n" in logo:
        raise SystemExit("el SVG del logotipo debe ser una sola línea sin comillas simples")

    items = json.dumps(reactivos, ensure_ascii=False)
    key = ofuscar(clave)
    extra = []
    ruta_ej = carpeta / "datos" / "ejemplos.json"
    if ruta_ej.exists():
        ejemplos = json.loads(leer(ruta_ej))
        if not set(ejemplos) <= set(reactivos):
            raise SystemExit(f"{carpeta.name}: ejemplos.json tiene series que no están en reactivos.json")
        extra += ["/* Ejemplos de práctica de datos/ejemplos.json; no cuentan para la calificación. */",
                  "const EJEMPLOS = " + json.dumps(ejemplos, ensure_ascii=False) + ";"]
    ruta_desc = carpeta / "datos" / "descripciones.json"
    if ruta_desc.exists():
        desc = json.loads(leer(ruta_desc))
        if list(desc) != list(reactivos) or any(len(desc[s]) != len(reactivos[s]) for s in reactivos):
            raise SystemExit(f"{carpeta.name}: descripciones.json y reactivos.json no tienen las mismas series y cantidades")
        extra += ["/* Descripciones de datos/descripciones.json para el prompt, ofuscadas como la clave. */",
                  'const DESC = JSON.parse(decodeURIComponent(escape(atob("' + ofuscar(desc) + '"))));']
    datos = "\n".join([
        "/* Logotipo de marca/logo-amador-russell.svg; cada pieza tiene su clase lg-* para la animación de la bienvenida. */",
        "const LOGO = '" + logo + "';",
        "/* Reactivos de datos/reactivos.json. FORM_ID sale de ellos: cambiar uno cambia la versión de la forma. */",
        "const ITEMS = " + items + ";",
        "/* Clave de datos/clave.json, ofuscada para que no quede legible en el HTML. */",
        'const KEY = JSON.parse(decodeURIComponent(escape(atob("' + key + '"))));',
    ] + extra)
    script = "\n".join([
        '"use strict";',
        "/* Generado por herramientas/construir.py. No lo edites a mano: cambia motor/, src/config.js, datos/ o marca/ y vuelve a construir. */",
        config.rstrip("\n"),
        datos,
        leer(MOTOR / "sesion.js").rstrip("\n"),
        leer(MOTOR / "motor.js").rstrip("\n"),
    ])
    if re.search(r"</script", script, re.I):
        raise SystemExit(f"{carpeta.name}: el script contiene </script y rompería la página")
    estilos = leer(MOTOR / "fuentes.css") + leer(MOTOR / "motor.css")
    piezas = {"TITULO": html.escape(titulo, quote=False), "ESTILOS": estilos.rstrip("\n"), "SCRIPT": script}
    plantilla = leer(MOTOR / "plantilla.html")
    for nombre in piezas:
        if plantilla.count("{{" + nombre + "}}") != 1:
            raise SystemExit(f"motor/plantilla.html debe tener {{{{{nombre}}}}} una sola vez")
    return re.sub(r"\{\{(TITULO|ESTILOS|SCRIPT)\}\}", lambda m: piezas[m.group(1)], plantilla).rstrip("\n") + "\n"


def construir_menu():
    actual = leer(MENU)
    if len(REGION.findall(actual)) != 1:
        raise SystemExit("sitio/index.html debe tener una sola región de motor/sesion.js entre sus marcas")
    return REGION.sub(lambda m: m.group(1) + leer(MOTOR / "sesion.js") + m.group(3), actual)


def main():
    verificar = "--verificar" in sys.argv[1:]
    carpetas = sorted(p.parent.parent for p in (RAIZ / "pruebas").glob("*/src/config.js"))
    if not carpetas:
        raise SystemExit("no hay pruebas con src/config.js")
    viejas = []
    objetivos = [(carpeta / "src" / "prueba.html", lambda c=carpeta: construir(c)) for carpeta in carpetas]
    objetivos.append((MENU, construir_menu))
    for destino, generar in objetivos:
        nuevo = generar()
        actual = leer(destino) if destino.exists() else None
        if verificar:
            if actual != nuevo:
                viejas.append(destino.relative_to(RAIZ).as_posix())
        elif actual != nuevo:
            destino.write_text(nuevo, encoding="utf-8")
            print("Construida:", destino.relative_to(RAIZ).as_posix())
        else:
            print("Sin cambios:", destino.relative_to(RAIZ).as_posix())
    if viejas:
        print("No coinciden con su construcción:\n- " + "\n- ".join(viejas))
        print("Se editó un archivo generado a mano o falta construir. Pasa el cambio a motor/, src/config.js o datos/ y corre: python herramientas/construir.py")
        sys.exit(1)
    if verificar:
        print(f"OK: {len(carpetas)} prueba(s) y el menú al día con su construcción")


if __name__ == "__main__":
    main()
