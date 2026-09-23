"""Vectoriza marca/logo-amador-russell.png en piezas animables.

Separa el logotipo por color y por forma (barra, franjas, aro y corona de la piña,
relleno amarillo y letras), traza cada pieza con potrace y escribe
marca/logo-amador-russell.svg. Ese SVG se copia en la constante LOGO de cada
src/prueba.html; las animaciones viven en el CSS de la prueba (clases lg-*).

Requiere pillow, numpy, scipy y el binario potrace.
    python marca/vectorizar_logo.py
"""
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
from scipy.spatial import ConvexHull

AQUI = Path(__file__).resolve().parent
PNG = AQUI / "logo-amador-russell.png"
SVG = AQUI / "logo-amador-russell.svg"
VERDE, AMARILLO, NEGRO = (21, 87, 80), (249, 212, 8), (3, 4, 5)
ARO = 44  # el aro de la piña está entre 27 y 43 px del relleno amarillo
OPT = "0.4"  # tolerancia de optimización de curvas de potrace
SUAVE = 0.6  # radio del suavizado antes de trazar, en píxeles


def cobertura(rgb, color):
    """Fracción de 'color' en cada píxel compuesto sobre blanco (0 a 1)."""
    blanco = np.array([255.0, 255, 255])
    eje = blanco - np.array(color, float)
    d = blanco - rgb
    t = np.clip((d @ eje) / (eje @ eje), 0, 1)
    fuera = np.linalg.norm(d - t[..., None] * eje, axis=-1)
    return np.where(fuera < 40, t, 0.0)


def componentes(mascara, minimo):
    lab, n = nd.label(mascara)
    tam = nd.sum(mascara, lab, range(1, n + 1))
    return lab, [i + 1 for i, s in enumerate(tam) if s >= minimo]


def envolvente(mascara):
    pts = np.argwhere(mascara)[:, ::-1]
    im = Image.new("1", mascara.shape[::-1], 0)
    ImageDraw.Draw(im).polygon([tuple(map(float, pts[i])) for i in ConvexHull(pts).vertices], fill=1)
    return np.array(im)


def x_min(mascara):
    return np.argwhere(mascara)[:, 1].min()


def main():
    rgba = np.array(Image.open(PNG).convert("RGBA")).astype(float)
    alfa = rgba[..., 3:] / 255
    rgb = rgba[..., :3] * alfa + 255 * (1 - alfa)
    filas = np.arange(rgb.shape[0])[:, None]
    # En la corona, la línea oscura entre hojas y franjas cuenta como verde; la separación la da la sombra del SVG.
    cob = {"v": np.maximum(cobertura(rgb, VERDE), cobertura(rgb, NEGRO) * (filas < 300)) > 0.5,
           "a": cobertura(rgb, AMARILLO) > 0.5,
           "n": cobertura(rgb, NEGRO) > 0.5}
    piezas = {}  # nombre -> núcleo de la pieza

    lab, ids = componentes(cob["a"], 1000)
    for i in ids:
        piezas["cuerpo" if np.argwhere(lab == i)[:, 0].min() > 400 else "domo"] = lab == i

    # Aro: el verde a distancia fija del relleno amarillo. Así queda completo aunque toque las franjas.
    dist = nd.distance_transform_edt(~envolvente(cob["a"]))
    lab, ids = componentes(cob["v"] & (dist <= ARO), 1000)
    piezas["aro"] = lab == max(ids, key=lambda i: (lab == i).sum())

    # Para separar piezas se usa solo el verde puro; los bordes suavizados se reparten después.
    puro = (np.linalg.norm(rgba[..., :3] - VERDE, axis=-1) < 40) & (alfa[..., 0] > 0.9)
    resto = puro & ~piezas["aro"]
    resto[:60, 255:262] = False  # separa la punta de la A (hoja central) de la barra superior
    nucleo = nd.binary_erosion(resto, iterations=2)  # rompe los puentes de 1 a 2 px entre hojas y franjas
    lab, ids = componentes(nucleo, 150)
    a_sup = lab == lab[45, 400]
    piezas["corona"] = np.isin(lab, [i for i in ids if i != lab[45, 400] and np.argwhere(lab == i)[:, 0].min() < 300])
    piezas["barra"] = a_sup & (filas <= 51)
    lab_s, ids_s = componentes(a_sup & ~piezas["barra"], 200)
    for k, i in enumerate(sorted(ids_s, key=lambda i: x_min(lab_s == i))):
        piezas[f"franja{k}"] = lab_s == i
    abajo = [lab == i for i in ids if np.argwhere(lab == i)[:, 0].min() > 400 and (lab == i).sum() >= 1000]
    for k, m in enumerate(sorted(abajo, key=x_min)):
        piezas[f"abajo{k}"] = m

    lab, ids = componentes(cob["n"] & (filas >= 350) & (filas < 430), 150)
    for k, i in enumerate(sorted(ids, key=lambda i: x_min(lab == i))):
        piezas[f"letra{k:02d}"] = lab == i

    # Cada píxel de un color va a la pieza más cercana de ese color.
    color_de = lambda n: "a" if n in ("cuerpo", "domo") else "n" if n.startswith("letra") else "v"
    salida = {}
    for c in "van":
        nombres = [n for n in piezas if color_de(n) == c]
        etiqueta = np.zeros(rgb.shape[:2], np.int32)
        for j, n in enumerate(nombres, 1):
            etiqueta[piezas[n]] = j
        distancia, (iy, ix) = nd.distance_transform_edt(etiqueta == 0, return_indices=True)
        cercana = etiqueta[iy, ix]
        for j, n in enumerate(nombres, 1):
            # Solapa 1 px con las piezas vecinas del mismo color para que no quede línea entre ellas, y
            # suaviza cada pieza por separado para no cerrar las líneas blancas entre piezas.
            pieza = cob[c] & nd.binary_dilation((cercana == j) & (distancia < 6))
            salida[n] = nd.gaussian_filter(pieza.astype(np.float32), SUAVE) > 0.5

    trazos = {n: trazar(m) for n, m in salida.items()}
    SVG.write_text(armar(trazos), encoding="utf-8")
    print(f"{SVG.name}: {len(trazos)} piezas, {SVG.stat().st_size} bytes")


def trazar(mascara):
    """Traza una máscara; devuelve el 'd' de potrace y la matriz que lo lleva a coordenadas del PNG."""
    ys, xs = np.nonzero(mascara)
    y0, y1, x0, x1 = ys.min() - 2, ys.max() + 3, xs.min() - 2, xs.max() + 3
    with tempfile.TemporaryDirectory() as tmp:
        pbm = Path(tmp) / "p.pbm"
        Image.fromarray(np.where(mascara[y0:y1, x0:x1], 0, 255).astype(np.uint8)).convert("1").save(pbm)
        svg = subprocess.run(["potrace", "-b", "svg", "--flat", "-t", "20", "-O", OPT, "-u", "4", "-o", "-", str(pbm)],
                             check=True, capture_output=True, text=True).stdout
    tx, ty, sx, sy = map(float, re.search(r"translate\(([-\d.]+),([-\d.]+)\) scale\(([-\d.]+),([-\d.]+)\)", svg).groups())
    d = re.sub(r"\s+", " ", " ".join(re.findall(r'd="([^"]+)"', svg))).strip()
    return d, (sx, sy, tx + x0, ty + y0)


def armar(trazos):
    """Arma el SVG con una clase por pieza; las animaciones viven en el CSS de la prueba."""
    def g(n, clase, d=None, ident=False):
        ruta, (a, b, e, f) = trazos[n]
        estilo = f' style="--d:{d}"' if d is not None else ""
        idp = f' id="lg-{n}"' if ident else ""
        return f'<g class="{clase}"{estilo}><path{idp} transform="matrix({a:g} 0 0 {b:g} {e:g} {f:g})" d="{ruta}"/></g>'

    franjas = sorted(n for n in trazos if n.startswith("franja"))
    abajo = sorted(n for n in trazos if n.startswith("abajo"))
    letras = sorted(n for n in trazos if n.startswith("letra"))
    verde, amarillo, negro = (f"rgb({c[0]},{c[1]},{c[2]})" for c in (VERDE, AMARILLO, NEGRO))
    return "".join([
        '<svg xmlns="http://www.w3.org/2000/svg" class="logo" data-act="logo" viewBox="20 20 760 760" role="img" aria-label="Amador Russell">',
        '<defs>',
        '<filter id="lg-sombra" filterUnits="userSpaceOnUse" x="0" y="0" width="800" height="800">'
        '<feDropShadow dx="3" dy="4" stdDeviation="3" flood-color="#000" flood-opacity=".28"/></filter>',
        '<clipPath id="lg-clip"><use href="#lg-cuerpo"/><use href="#lg-domo"/></clipPath>',
        '<linearGradient id="lg-luz"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff" stop-opacity=".8"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        '</defs>',
        f'<g fill="{verde}" filter="url(#lg-sombra)">', g("barra", "lg-barra"),
        *[g(n, "lg-franja", k) for k, n in enumerate(franjas)],
        *[g(n, "lg-franja", k + 9) for k, n in enumerate(abajo)],  # cada franja de abajo sigue a la de arriba (k + 2)
        '</g>',
        f'<g fill="{verde}" filter="url(#lg-sombra)">', g("aro", "lg-aro"), g("corona", "lg-corona"), '</g>',
        f'<g fill="{amarillo}">', g("cuerpo", "lg-cuerpo", ident=True), g("domo", "lg-domo", ident=True), '</g>',
        '<g clip-path="url(#lg-clip)"><rect class="lg-brillo" x="-60" y="230" width="120" height="520" fill="url(#lg-luz)"/></g>',
        f'<g fill="{negro}" filter="url(#lg-sombra)">', *[g(n, "lg-letra", k) for k, n in enumerate(letras)], '</g>',
        '</svg>',
    ])


if __name__ == "__main__":
    main()
