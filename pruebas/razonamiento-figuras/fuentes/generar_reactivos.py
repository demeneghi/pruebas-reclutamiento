"""Genera los reactivos de Razonamiento con Figuras, Forma A.

Esta prueba no tiene cuadernillo externo: este script es su fuente. Cada reactivo se define por una regla
explícita sobre atributos (forma, relleno, cantidad, tamaño, giro, trazos) o por un patrón continuo, y se
dibuja como SVG. Las figuras son propias; no se calcó ni se adaptó ninguna lámina de pruebas publicadas.

Series:
- A: completar un patrón continuo (textura) con la pieza que falta. 6 opciones.
- B: analogía en matriz de 2 x 2 (lo que cambia en la fila y en la columna). 6 opciones.
- C: progresión en matriz de 3 x 3 (cantidad, tamaño, giro, lados). 8 opciones.
- D: distribución de tres valores en matriz de 3 x 3 (cada fila y columna tiene uno de cada uno). 8 opciones.
- E: suma, resta, diferencia y parte común de trazos en matriz de 3 x 3. 8 opciones.

Controles de respuesta única (fallan al generar si no se cumplen):
- B, C y D: las opciones son combinaciones de 2 o 3 atributos, cada uno con el valor correcto o uno
  incorrecto (6 = 2 x 3, 8 = 2 x 2 x 2). Cada valor aparece igual de seguido entre las opciones, así que
  contar qué rasgo se repite más no delata la respuesta. Solo una opción tiene todos los valores correctos.
- E: se prueban todas las reglas de trazos (suma, resta en ambos sentidos, diferencia, parte común y
  distribución) por filas y por columnas; toda regla que explique las filas o columnas completas debe
  predecir la misma respuesta.
- A: la prueba tests/test_reactivos.py dibuja cada opción y exige que difiera visualmente de las demás.

Posición de la respuesta correcta: balanceada con la semilla fija SEMILLA, igual para todos los candidatos.

Uso:
    python pruebas/razonamiento-figuras/fuentes/generar_reactivos.py
Escribe datos/reactivos.json, datos/clave.json, datos/descripciones.json y datos/ejemplos.json.
Después: python herramientas/construir.py
"""
import itertools
import json
import math
import random
from pathlib import Path

CARPETA = Path(__file__).resolve().parent.parent
SEMILLA = 20260923
TINTA = "#1C2633"


def n(x):
    """Número compacto para el SVG."""
    r = round(x, 1)
    return str(int(r)) if r == int(r) else str(r)


def pts_txt(pts):
    return " ".join(n(x) + "," + n(y) for x, y in pts)


class Ids:
    """Identificadores únicos y deterministas para los recortes (clipPath) de cada dibujo."""

    def __init__(self, prefijo):
        self.prefijo, self.k = prefijo, 0

    def nuevo(self):
        self.k += 1
        return f"{self.prefijo}k{self.k}"


# ====== Figuras ======

FORMAS = {
    "circulo": "círculo", "cuadrado": "cuadrado", "triangulo": "triángulo", "rombo": "rombo",
    "pentagono": "pentágono", "hexagono": "hexágono", "estrella": "estrella", "cruz": "cruz",
    "flecha": "flecha", "gancho": "gancho",
}


def regular(lados, escala, giro0):
    return [(escala * math.cos(math.radians(giro0 + 360 * k / lados)), escala * math.sin(math.radians(giro0 + 360 * k / lados))) for k in range(lados)]


PLANTILLAS = {
    "cuadrado": regular(4, 1.2, 45),
    "triangulo": [(x, y + 0.2) for x, y in regular(3, 1.3, -90)],
    "rombo": regular(4, 1.25, -90),
    "pentagono": regular(5, 1.12, -90),
    "hexagono": regular(6, 1.1, 0),
    "estrella": [(r * math.cos(math.radians(-90 + 36 * k)), r * math.sin(math.radians(-90 + 36 * k))) for k, r in zip(range(10), [1.25, 0.52] * 5)],
    "cruz": [(-0.33, -1.05), (0.33, -1.05), (0.33, -0.33), (1.05, -0.33), (1.05, 0.33), (0.33, 0.33), (0.33, 1.05), (-0.33, 1.05), (-0.33, 0.33), (-1.05, 0.33), (-1.05, -0.33), (-0.33, -0.33)],
    "flecha": [(0, -1.15), (0.78, -0.1), (0.3, -0.1), (0.3, 1.1), (-0.3, 1.1), (-0.3, -0.1), (-0.78, -0.1)],
    "gancho": [(-0.65, -1.1), (-0.15, -1.1), (-0.15, 0.6), (0.75, 0.6), (0.75, 1.1), (-0.65, 1.1)],
}


def puntos_forma(forma, cx, cy, r, giro=0, espejo=False):
    out = []
    a = math.radians(giro)
    for x, y in PLANTILLAS[forma]:
        if espejo:
            x = -x
        x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        out.append((cx + r * x, cy + r * y))
    return out


def contorno(forma, cx, cy, r, giro, espejo, estilo):
    if forma == "circulo":
        return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"{estilo}/>'
    return f'<polygon points="{pts_txt(puntos_forma(forma, cx, cy, r, giro, espejo))}"{estilo}/>'


def trazo(g=3):
    return f' stroke="{TINTA}" stroke-width="{n(g)}" stroke-linejoin="round"'


def figura(ids, forma, cx, cy, r, relleno="blanco", giro=0, espejo=False, g=3):
    """Una figura con su relleno: blanco, negro, rayas (diagonales), rayas_h, rayas_v o mitad_<lado>."""
    if relleno == "blanco":
        return contorno(forma, cx, cy, r, giro, espejo, ' fill="#fff"' + trazo(g))
    if relleno == "negro":
        return contorno(forma, cx, cy, r, giro, espejo, f' fill="{TINTA}"' + trazo(g))
    k = ids.nuevo()
    recorte = f'<clipPath id="{k}">' + contorno(forma, cx, cy, r, giro, espejo, "") + "</clipPath>"
    m = r * 1.4
    if relleno.startswith("mitad_"):
        lado = relleno[6:]
        x0, y0, w, h = {"izq": (cx - m, cy - m, m, 2 * m), "der": (cx, cy - m, m, 2 * m),
                        "arriba": (cx - m, cy - m, 2 * m, m), "abajo": (cx - m, cy, 2 * m, m)}[lado]
        dentro = f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{n(h)}" fill="{TINTA}"/>'
    else:
        paso = max(5.0, r / 3.2)
        lineas = []
        t = -2 * m
        while t <= 2 * m:
            if relleno == "rayas_h":
                lineas.append((cx - m, cy + t, cx + m, cy + t))
            elif relleno == "rayas_v":
                lineas.append((cx + t, cy - m, cx + t, cy + m))
            else:
                lineas.append((cx + t - m, cy + m, cx + t + m, cy - m))
            t += paso
        dentro = "".join(f'<line x1="{n(a)}" y1="{n(b)}" x2="{n(c)}" y2="{n(d)}" stroke="{TINTA}" stroke-width="2"/>' for a, b, c, d in lineas)
    return recorte + contorno(forma, cx, cy, r, giro, espejo, ' fill="#fff"') + f'<g clip-path="url(#{k})">{dentro}</g>' + contorno(forma, cx, cy, r, giro, espejo, ' fill="none"' + trazo(g))


# ====== Celdas de las matrices (series B a E) ======

TAM = {"S": 15, "M": 25, "L": 35}
TAM_VARIAS = {"S": 7.5, "M": 10.5, "L": 13}
ACOMODO = {
    1: [(50, 50)], 2: [(30, 50), (70, 50)], 3: [(20, 50), (50, 50), (80, 50)],
    4: [(29, 29), (71, 29), (29, 71), (71, 71)], 5: [(27, 27), (73, 27), (50, 50), (27, 73), (73, 73)],
    6: [(20, 30), (50, 30), (80, 30), (20, 70), (50, 70), (80, 70)],
}
POS = {"TL": (28, 28), "TR": (72, 28), "BR": (72, 72), "BL": (28, 72), "C": (50, 50)}
TRAZOS = {
    "arriba": ((14, 14), (86, 14)), "abajo": ((14, 86), (86, 86)), "izq": ((14, 14), (14, 86)), "der": ((86, 14), (86, 86)),
    "diag1": ((14, 14), (86, 86)), "diag2": ((86, 14), (14, 86)), "horiz": ((14, 50), (86, 50)), "vert": ((50, 14), (50, 86)),
}
NOM_TRAZOS = {"arriba": "línea arriba", "abajo": "línea abajo", "izq": "línea izquierda", "der": "línea derecha",
              "diag1": "diagonal \\", "diag2": "diagonal /", "horiz": "línea horizontal al centro",
              "vert": "línea vertical al centro", "circ": "círculo", "punto": "punto"}
BASE = {"forma": "circulo", "relleno": "blanco", "tam": "M", "n": 1, "giro": 0, "espejo": False,
        "interior": None, "pos": None, "anillos": None, "lineas": None, "orient": "h", "grueso": False, "trazos": None, "arriba": None, "abajo": None, "varias": False}


def celda(ids, a):
    a = {**BASE, **a}
    s = []
    if a["trazos"] is not None:
        for t in sorted(a["trazos"]):
            if t == "circ":
                s.append(f'<circle cx="50" cy="50" r="22" fill="none"{trazo(3.5)}/>')
            elif t == "punto":
                s.append(f'<circle cx="50" cy="50" r="9" fill="{TINTA}"/>')
            else:
                (x1, y1), (x2, y2) = TRAZOS[t]
                s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{TINTA}" stroke-width="3.5" stroke-linecap="round"/>')
        return "".join(s)
    if a["lineas"] is not None:
        k, orient, g = a["lineas"], a["orient"], 9 if a["grueso"] else 4
        for i in range(k):
            d = (i - (k - 1) / 2) * 18
            if orient == "h":
                s.append(f'<line x1="18" y1="{n(50 + d)}" x2="82" y2="{n(50 + d)}"{trazo(g)} stroke-linecap="round"/>')
            elif orient == "v":
                s.append(f'<line x1="{n(50 + d)}" y1="18" x2="{n(50 + d)}" y2="82"{trazo(g)} stroke-linecap="round"/>')
            else:
                o = d / math.sqrt(2)
                s.append(f'<line x1="{n(26 + o)}" y1="{n(74 + o)}" x2="{n(74 + o)}" y2="{n(26 + o)}"{trazo(g)} stroke-linecap="round"/>')
        return "".join(s)
    if a["anillos"] is not None:
        radios = [36, 25, 14][: a["anillos"]]
        for i, r in enumerate(radios):
            ultimo = i == len(radios) - 1
            s.append(figura(ids, a["forma"], 50, 50, r, a["relleno"] if ultimo else "blanco"))
        return "".join(s)
    if a["arriba"] is not None:
        s.append(figura(ids, a["arriba"], 50, 28, 17, a["relleno"]))
        s.append(figura(ids, a["abajo"], 50, 72, 17, "blanco"))
        return "".join(s)
    if a["pos"] is not None:
        s.append(f'<rect x="10" y="10" width="80" height="80" fill="none"{trazo(2)}/>')
        x, y = POS[a["pos"]]
        s.append(figura(ids, a["forma"], x, y, 13, a["relleno"], a["giro"], a["espejo"]))
        return "".join(s)
    if a["n"] == 1 and not a["varias"]:
        r = TAM[a["tam"]]
        s.append(figura(ids, a["forma"], 50, 50, r, a["relleno"], a["giro"], a["espejo"]))
        if a["interior"]:
            i = a["interior"]
            if i == "punto":
                s.append(f'<circle cx="50" cy="50" r="7" fill="{TINTA}"/>')
            elif i == "barra":
                s.append(f'<rect x="36" y="46.5" width="28" height="7" fill="{TINTA}"/>')
            elif i == "cruzeta":
                s.append(f'<path d="M50 37V63M37 50H63" stroke="{TINTA}" stroke-width="5"/>')
            else:
                s.append(figura(ids, i, 50, 50, r * 0.42, "blanco", 0, False, 2.5))
        return "".join(s)
    r = TAM_VARIAS[a["tam"]]
    for x, y in ACOMODO[a["n"]]:
        s.append(figura(ids, a["forma"], x, y, r, a["relleno"], a["giro"], a["espejo"], 2.5))
    return "".join(s)


RELLENOS = {"blanco": "blanco", "negro": "negro", "rayas": "con rayas diagonales", "rayas_h": "con rayas horizontales",
            "rayas_v": "con rayas verticales", "mitad_izq": "mitad izquierda negra", "mitad_der": "mitad derecha negra",
            "mitad_arriba": "mitad de arriba negra", "mitad_abajo": "mitad de abajo negra"}
INTERIOR = {"punto": "punto", "barra": "barra", "cruzeta": "cruz pequeña"}
POS_TXT = {"TL": "arriba a la izquierda", "TR": "arriba a la derecha", "BR": "abajo a la derecha", "BL": "abajo a la izquierda", "C": "al centro"}
TAM_TXT = {"S": "chico", "M": "mediano", "L": "grande"}
ORIENT_TXT = {"h": "horizontales", "v": "verticales", "d": "diagonales"}


def describir(a):
    """Descripción en texto de una celda, para el prompt."""
    a = {**BASE, **a}
    if a["trazos"] is not None:
        return ", ".join(NOM_TRAZOS[t] for t in sorted(a["trazos"], key=list(NOM_TRAZOS).index)) or "vacía"
    if a["lineas"] is not None:
        k, o = a["lineas"], a["orient"]
        return f"{k} línea{'s' if k > 1 else ''} {ORIENT_TXT[o] if k > 1 else ORIENT_TXT[o][:-2]}{' gruesa' + ('s' if k > 1 else '') if a['grueso'] else ''}"
    f = FORMAS[a["forma"]]
    rel = RELLENOS[a["relleno"]]
    if a["anillos"] is not None:
        return f"{a['anillos']} {f}{'s' if a['anillos'] > 1 else ''} uno dentro de otro, el del centro {rel}"
    if a["arriba"] is not None:
        return f"{FORMAS[a['arriba']]} {rel} arriba y {FORMAS[a['abajo']]} abajo"
    partes = []
    if a["pos"] is not None:
        partes.append(f"{f} {rel} {POS_TXT[a['pos']]} del marco")
    elif a["n"] == 1 and not a["varias"]:
        partes.append(f"{f} {rel} {TAM_TXT[a['tam']]}")
        if a["interior"]:
            partes.append("con " + (INTERIOR.get(a["interior"]) or FORMAS[a["interior"]]) + " adentro")
    else:
        pl = "s" if a["n"] > 1 else ""
        partes.append(f"{a['n']} {f}{pl} {rel.replace('blanco', 'blanco' + pl).replace('negro', 'negro' + pl)} {TAM_TXT[a['tam']]}{pl}")
    if a["espejo"]:
        partes.append("en espejo")
    if a["giro"]:
        partes.append(f"girada {a['giro']}° a la derecha")
    return ", ".join(partes)


# ====== Posición balanceada de la respuesta correcta ======

def posiciones(rng, cantidad, opciones):
    """Posición de la respuesta en cada reactivo: cada posición casi el mismo número de veces,
    sin la misma posición en dos reactivos seguidos."""
    base = [k % opciones for k in range(cantidad)]
    while True:
        rng.shuffle(base)
        if all(base[i] != base[i + 1] for i in range(len(base) - 1)):
            return base


def ordenar(rng, correcta, distractores, pos):
    d = distractores[:]
    rng.shuffle(d)
    return d[:pos] + [correcta] + d[pos:]


# ====== Series B, C y D: matrices de atributos ======

def combinaciones(respuesta, variar):
    """Opciones = todas las combinaciones de los valores (correcto o alternativos) de los atributos a variar."""
    ejes = [[{attr: respuesta.get(attr, BASE[attr])}] + [v if isinstance(v, dict) else {attr: v} for v in alts] for attr, alts in variar]
    ops = []
    for combo in itertools.product(*ejes):
        o = dict(respuesta)
        for cambio in combo:
            o.update(cambio)
        ops.append(o)
    claves = [json.dumps({**BASE, **o}, sort_keys=True, default=sorted) for o in ops]
    if len(set(claves)) != len(claves):
        raise SystemExit(f"opciones repetidas: {variar}")
    return ops[0], ops[1:]


def matriz(codigo, celdas, respuesta, variar, regla, rng, pos):
    """celdas: lista de atributos por celda (la última es la que falta)."""
    ids = Ids(codigo)
    if {**BASE, **celdas[-1]} != {**BASE, **respuesta}:
        raise SystemExit(f"{codigo}: la celda que falta no coincide con la respuesta")
    correcta, distractores = combinaciones(respuesta, variar)
    orden = ordenar(rng, correcta, distractores, pos)
    return ({"celdas": [celda(ids, c) for c in celdas[:-1]] + [None], "opciones": [celda(ids, o) for o in orden]},
            pos, {"regla": regla, "opciones": [describir(o) for o in orden]})


def analogia(codigo, a, fila, col, variar, regla, rng, pos):
    """Matriz de 2 x 2: fila y columna son cambios que conmutan; la celda que falta es fila(col(a))."""
    b, c = fila(dict(a)), col(dict(a))
    d1, d2 = fila(col(dict(a))), col(fila(dict(a)))
    if {**BASE, **d1} != {**BASE, **d2}:
        raise SystemExit(f"{codigo}: los cambios de fila y columna no conmutan")
    return matriz(codigo, [a, b, c, d1], d1, variar, regla, rng, pos)


def cambia(**cambios):
    def f(a):
        out = dict(a)
        for k, v in cambios.items():
            out[k] = v(out.get(k, BASE[k])) if callable(v) else v
        return out
    return f


def tabla(codigo, fn, variar, regla, rng, pos):
    """Matriz de 3 x 3 con atributos fn(fila, columna)."""
    celdas = [fn(i, j) for i in range(3) for j in range(3)]
    return matriz(codigo, celdas, celdas[-1], variar, regla, rng, pos)


L1 = [[0, 1, 2], [1, 2, 0], [2, 0, 1]]
L2 = [[0, 1, 2], [2, 0, 1], [1, 2, 0]]


def serie_b(rng, pos):
    it = []
    it.append(analogia("B01", {"forma": "circulo"}, cambia(relleno="negro"), cambia(forma="cuadrado"),
                       [("relleno", ["blanco"]), ("forma", ["circulo", "triangulo"])],
                       "En la fila la figura se rellena de negro; en la columna el círculo cambia a cuadrado.", rng, pos[0]))
    it.append(analogia("B02", {"forma": "triangulo", "tam": "S"}, cambia(tam="L"), cambia(forma="hexagono"),
                       [("tam", ["S"]), ("forma", ["triangulo", "cuadrado"])],
                       "En la fila la figura crece de chica a grande; en la columna el triángulo cambia a hexágono.", rng, pos[1]))
    it.append(analogia("B03", {"forma": "flecha", "tam": "L"}, cambia(giro=lambda g: (g + 90) % 360), cambia(relleno="negro"),
                       [("relleno", ["blanco"]), ("giro", [0, 270])],
                       "En la fila la flecha gira un cuarto de vuelta a la derecha; en la columna se rellena de negro.", rng, pos[2]))
    it.append(analogia("B04", {"forma": "circulo", "relleno": "negro", "tam": "L", "varias": True}, cambia(n=3), cambia(forma="rombo"),
                       [("n", [1]), ("forma", ["circulo", "cuadrado"])],
                       "En la fila una figura se vuelve tres; en la columna el círculo cambia a rombo.", rng, pos[3]))
    it.append(analogia("B05", {"forma": "cuadrado", "tam": "L"}, cambia(interior="punto"), cambia(forma="circulo"),
                       [("interior", [None]), ("forma", ["cuadrado", "hexagono"])],
                       "En la fila aparece un punto adentro; en la columna el cuadrado cambia a círculo.", rng, pos[4]))
    it.append(analogia("B06", {"forma": "triangulo", "relleno": "negro", "pos": "TL"}, cambia(pos="TR"), cambia(forma="circulo"),
                       [("forma", ["triangulo"]), ("pos", ["TL", "BR"])],
                       "En la fila la figura pasa de la esquina izquierda a la derecha; en la columna el triángulo cambia a círculo.", rng, pos[5]))
    mapa = {"cuadrado": "triangulo", "circulo": "rombo"}
    it.append(analogia("B07", {"forma": "cuadrado", "tam": "L", "interior": "circulo"},
                       lambda a: {**a, "forma": a["interior"], "interior": a["forma"]},
                       lambda a: {**a, "forma": mapa[a["forma"]], "interior": mapa[a["interior"]]},
                       [("forma", ["triangulo"]), ("interior", ["rombo", "circulo"])],
                       "En la fila la figura de afuera y la de adentro cambian de lugar; en la columna el cuadrado cambia a triángulo y el círculo a rombo.", rng, pos[6]))
    it.append(analogia("B08", {"forma": "gancho", "tam": "L", "varias": True}, cambia(giro=lambda g: (g + 180) % 360), cambia(n=2),
                       [("n", [1]), ("giro", [0, 90])],
                       "En la fila la figura da media vuelta; en la columna una figura se vuelve dos.", rng, pos[7]))
    it.append(analogia("B09", {"forma": "gancho", "tam": "L"}, cambia(espejo=True), cambia(relleno="rayas"),
                       [("relleno", ["blanco"]), ("espejo", [False, {"espejo": True, "giro": 180}])],
                       "En la fila la figura se voltea como en un espejo; en la columna se rellena con rayas.", rng, pos[8]))
    it.append(analogia("B10", {"forma": "pentagono", "n": 4}, cambia(n=2), cambia(relleno="negro"),
                       [("relleno", ["blanco"]), ("n", [4, 3])],
                       "En la fila cuatro figuras se vuelven dos; en la columna se rellenan de negro.", rng, pos[9]))
    it.append(analogia("B11", {"forma": "circulo", "tam": "L", "relleno": "mitad_izq"},
                       cambia(relleno=lambda r: {"mitad_izq": "mitad_arriba"}[r]), cambia(forma="cuadrado"),
                       [("forma", ["circulo"]), ("relleno", ["mitad_izq", "mitad_abajo"])],
                       "En la fila la mitad negra gira un cuarto de vuelta a la derecha (de la izquierda pasa arriba); en la columna el círculo cambia a cuadrado.", rng, pos[10]))
    it.append(analogia("B12", {"forma": "flecha", "tam": "L", "varias": True}, cambia(giro=lambda g: (g + 90) % 360, relleno="negro"), cambia(n=2),
                       [("relleno", ["blanco"]), ("giro", [0, 180])],
                       "En la fila la flecha gira un cuarto de vuelta a la derecha y se rellena de negro; en la columna una flecha se vuelve dos.", rng, pos[11]))
    return it


def serie_c(rng, pos):
    it = []
    formas3 = ["circulo", "cuadrado", "triangulo"]
    it.append(tabla("C01", lambda i, j: {"forma": formas3[i], "n": j + 1, "tam": "L", "varias": True},
                    [("n", [2]), ("forma", ["cuadrado"]), ("relleno", ["negro"])],
                    "En cada fila la cantidad aumenta de uno en uno (1, 2, 3); cada fila tiene su propia figura.", rng, pos[0]))
    it.append(tabla("C02", lambda i, j: {"forma": ["rombo", "hexagono", "estrella"][i], "tam": "SML"[j], "relleno": ["blanco", "negro", "rayas"][i]},
                    [("tam", ["M"]), ("forma", ["hexagono"]), ("relleno", ["negro"])],
                    "En cada fila la figura crece (chica, mediana, grande); cada fila tiene su figura y su relleno.", rng, pos[1]))
    it.append(tabla("C03", lambda i, j: {"forma": "circulo", "relleno": "negro", "n": i + j + 1, "varias": True},
                    [("n", [4]), ("forma", ["cuadrado"]), ("relleno", ["blanco"])],
                    "La cantidad aumenta en uno hacia la derecha y en uno hacia abajo: la última casilla tiene 5.", rng, pos[2]))
    it.append(tabla("C04", lambda i, j: {"forma": "flecha", "tam": "L", "giro": (90 * i + 45 * j) % 360},
                    [("giro", [90]), ("relleno", ["negro"]), ("tam", ["M"])],
                    "La flecha gira un octavo de vuelta a la derecha en cada paso de la fila; cada fila empieza un cuarto de vuelta más girada.", rng, pos[3]))
    it.append(tabla("C05", lambda i, j: {"forma": ["triangulo", "cuadrado", "pentagono"][j], "relleno": ["blanco", "rayas", "negro"][i], "tam": "L"},
                    [("forma", ["cuadrado"]), ("relleno", ["rayas"]), ("tam", ["S"])],
                    "En cada fila la figura gana un lado (3, 4, 5); cada fila tiene su relleno.", rng, pos[4]))
    it.append(tabla("C06", lambda i, j: {"lineas": j + 1, "orient": "hvd"[i]},
                    [("lineas", [2]), ("orient", ["v"]), ("grueso", [True])],
                    "En cada fila aumenta el número de líneas (1, 2, 3); cada fila tiene su dirección: horizontales, verticales, diagonales.", rng, pos[5]))
    it.append(tabla("C07", lambda i, j: {"forma": ["circulo", "cuadrado", "hexagono"][i], "anillos": j + 1, "relleno": "negro"},
                    [("anillos", [2]), ("forma", ["cuadrado"]), ("relleno", ["blanco"])],
                    "En cada fila se agrega una figura dentro de la anterior (1, 2, 3); la del centro es negra; cada fila tiene su figura.", rng, pos[6]))
    orden = ["TL", "TR", "BR", "BL"]
    it.append(tabla("C08", lambda i, j: {"forma": "circulo", "relleno": "negro", "pos": orden[(i + j) % 4]},
                    [("pos", ["BR"]), ("forma", ["cuadrado"]), ("relleno", ["blanco"])],
                    "El círculo avanza una esquina en el sentido de las manecillas del reloj en cada paso a la derecha y en cada paso hacia abajo.", rng, pos[7]))
    it.append(tabla("C09", lambda i, j: {"forma": ["cuadrado", "circulo", "rombo"][i], "tam": "L", "relleno": ["blanco", "rayas_v", "negro"][j]},
                    [("relleno", ["rayas_v"]), ("forma", ["circulo"]), ("tam", ["M"])],
                    "En cada fila el relleno pasa de blanco a rayas y a negro; cada fila tiene su figura.", rng, pos[8]))
    it.append(tabla("C10", lambda i, j: {"forma": "estrella", "relleno": "negro", "n": j + 1, "tam": "SML"[i], "varias": True},
                    [("n", [2]), ("tam", ["M"]), ("forma", ["cruz"])],
                    "En cada fila la cantidad aumenta (1, 2, 3); hacia abajo las figuras crecen (chicas, medianas, grandes).", rng, pos[9]))
    it.append(tabla("C11", lambda i, j: {"forma": "flecha", "n": j + 1, "tam": "L", "giro": 90 * i, "varias": True},
                    [("n", [2]), ("giro", [90]), ("relleno", ["negro"])],
                    "En cada fila aumenta la cantidad de flechas (1, 2, 3); hacia abajo las flechas giran un cuarto de vuelta a la derecha en cada fila.", rng, pos[10]))
    it.append(tabla("C12", lambda i, j: {"forma": ["triangulo", "cuadrado", "pentagono"][j], "n": i + 2, "tam": "M", "relleno": "rayas"},
                    [("n", [3]), ("forma", ["cuadrado"]), ("relleno", ["blanco"])],
                    "Hacia la derecha la figura gana un lado (3, 4, 5); hacia abajo aumenta la cantidad (2, 3, 4).", rng, pos[11]))
    return it


def serie_d(rng, pos):
    it = []
    f3 = ["circulo", "cuadrado", "triangulo"]
    it.append(tabla("D01", lambda i, j: {"forma": f3[L1[i][j]], "relleno": ["blanco", "rayas", "negro"][i], "tam": "L"},
                    [("forma", ["triangulo"]), ("relleno", ["rayas"]), ("tam", ["S"])],
                    "Cada fila y cada columna tienen un círculo, un cuadrado y un triángulo; cada fila tiene su relleno.", rng, pos[0]))
    it.append(tabla("D02", lambda i, j: {"forma": ["rombo", "hexagono", "cruz"][L1[i][j]], "relleno": ["blanco", "negro", "rayas"][L2[i][j]], "tam": "L"},
                    [("forma", ["cruz"]), ("relleno", ["negro"]), ("tam", ["M"])],
                    "Cada fila y cada columna tienen un rombo, un hexágono y una cruz, y también un relleno blanco, uno negro y uno con rayas.", rng, pos[1]))
    it.append(tabla("D03", lambda i, j: {"forma": ["cuadrado", "triangulo", "circulo"][i], "relleno": "negro", "n": 1 + L1[i][j], "tam": "L", "varias": True},
                    [("n", [3]), ("forma", ["triangulo"]), ("relleno", ["blanco"])],
                    "Cada fila y cada columna tienen una, dos y tres figuras; cada fila tiene su figura.", rng, pos[2]))
    it.append(tabla("D04", lambda i, j: {"forma": ["pentagono", "circulo", "estrella"][L2[i][j]], "tam": "SML"[L1[i][j]]},
                    [("forma", ["circulo"]), ("tam", ["S"]), ("relleno", ["negro"])],
                    "Cada fila y cada columna tienen un pentágono, un círculo y una estrella, y también una figura chica, una mediana y una grande.", rng, pos[3]))
    it.append(tabla("D05", lambda i, j: {"forma": ["circulo", "cuadrado", "rombo"][L1[i][j]], "tam": "L", "interior": ["punto", "barra", "cruzeta"][L2[i][j]]},
                    [("forma", ["circulo"]), ("interior", ["barra"]), ("tam", ["M"])],
                    "Cada fila y cada columna tienen un círculo, un cuadrado y un rombo, y adentro un punto, una barra y una cruz pequeña.", rng, pos[4]))
    it.append(tabla("D06", lambda i, j: {"forma": "flecha", "tam": "L", "giro": [0, 90, 180][L1[i][j]], "relleno": ["blanco", "negro", "rayas"][L2[i][j]]},
                    [("giro", [180]), ("relleno", ["negro"]), ("tam", ["M"])],
                    "Cada fila y cada columna tienen una flecha hacia arriba, una a la derecha y una hacia abajo, y también un relleno blanco, uno negro y uno con rayas.", rng, pos[5]))
    it.append(tabla("D07", lambda i, j: {"forma": ["triangulo", "cuadrado", "hexagono"][L1[i][j]], "relleno": ["negro", "blanco", "rayas"][L2[i][j]], "n": 1 + (i + j + 1) % 3, "tam": "L", "varias": True},
                    [("forma", ["triangulo"]), ("relleno", ["rayas"]), ("n", [2])],
                    "Cada fila y cada columna tienen triángulos, cuadrados y hexágonos; rellenos negro, blanco y con rayas; y una, dos y tres figuras.", rng, pos[6]))
    it.append(tabla("D08", lambda i, j: {"forma": ["circulo", "estrella", "cuadrado"][L2[i][j]], "relleno": "negro", "pos": ["TL", "TR", "BR"][L1[i][j]]},
                    [("pos", ["TL"]), ("forma", ["estrella"]), ("relleno", ["blanco"])],
                    "Cada fila y cada columna tienen la figura en tres esquinas distintas (arriba a la izquierda, arriba a la derecha, abajo a la derecha) y tres figuras distintas: círculo, estrella y cuadrado.", rng, pos[7]))
    it.append(tabla("D09", lambda i, j: {"lineas": [1, 2, 3][L2[i][j]], "orient": "hvd"[L1[i][j]]},
                    [("lineas", [2]), ("orient", ["h"]), ("grueso", [True])],
                    "Cada fila y cada columna tienen líneas horizontales, verticales y diagonales, y también una, dos y tres líneas.", rng, pos[8]))
    it.append(tabla("D10", lambda i, j: {"forma": ["hexagono", "circulo", "triangulo"][L2[i][j]], "anillos": 2, "relleno": ["blanco", "negro", "rayas"][L1[i][j]]},
                    [("forma", ["circulo"]), ("relleno", ["rayas"]), ("anillos", [3])],
                    "Cada fila y cada columna tienen hexágonos, círculos y triángulos, y el centro blanco, negro y con rayas.", rng, pos[9]))
    it.append(tabla("D11", lambda i, j: {"forma": ["cuadrado", "rombo", "circulo"][L1[i][j]], "relleno": ["rayas", "blanco", "negro"][L2[i][j]], "tam": "SML"[(L2[i][j] + 1) % 3]},
                    [("forma", ["circulo"]), ("relleno", ["negro"]), ("tam", ["L"])],
                    "Cada fila y cada columna tienen cuadrado, rombo y círculo; rellenos con rayas, blanco y negro; y tamaños chico, mediano y grande.", rng, pos[10]))
    it.append(tabla("D12", lambda i, j: {"arriba": ["circulo", "cuadrado", "triangulo"][L1[i][j]], "abajo": ["rombo", "estrella", "cruz"][L2[i][j]], "relleno": ["negro", "rayas", "blanco"][(L1[i][j] + 1) % 3]},
                    [("arriba", ["circulo"]), ("abajo", ["estrella"]), ("relleno", ["negro"])],
                    "Cada fila y cada columna tienen arriba un círculo, un cuadrado y un triángulo; abajo un rombo, una estrella y una cruz; y la figura de arriba negra, con rayas y blanca.", rng, pos[11]))
    return it


# ====== Serie E: trazos ======

OPS = {
    "suma": lambda a, b: a | b,
    "resta": lambda a, b: a - b,
    "resta_inversa": lambda a, b: b - a,
    "diferencia": lambda a, b: a ^ b,
    "comun": lambda a, b: a & b,
}
REGLAS_E = {
    "suma": "La tercera casilla de cada fila junta los trazos de las dos primeras.",
    "resta": "La tercera casilla de cada fila es la primera sin los trazos de la segunda.",
    "diferencia": "La tercera casilla de cada fila tiene los trazos que están en una sola de las dos primeras; los que se repiten desaparecen.",
    "comun": "La tercera casilla de cada fila tiene solo los trazos que se repiten en las dos primeras.",
}


def predicciones(m):
    """Respuestas que predice toda regla de trazos que explique las filas (o columnas) completas."""
    pred = set()
    for direccion in ("filas", "columnas"):
        g = m if direccion == "filas" else [[m[j][i] for j in range(3)] for i in range(3)]
        for op in OPS.values():
            if all(op(g[i][0], g[i][1]) == g[i][2] for i in range(2)):
                pred.add(frozenset(op(g[2][0], g[2][1])))
        # Distribución: cada fila contiene las mismas tres figuras en otro orden.
        if sorted(map(sorted, g[0])) == sorted(map(sorted, g[1])):
            resto = [x for x in g[0] if x not in (g[2][0], g[2][1])]
            if len(resto) == 1:
                pred.add(frozenset(resto[0]))
    return pred


def serie_e(rng, pos):
    todos = list(TRAZOS) + ["circ", "punto"]
    plan = [("suma", 1, 1), ("suma", 1, 2), ("resta", 2, 1), ("suma", 2, 2), ("resta", 3, 1), ("diferencia", 2, 2),
            ("resta", 4, 2), ("diferencia", 2, 3), ("comun", 3, 3), ("diferencia", 3, 3), ("comun", 4, 3), ("diferencia", 4, 4)]
    it = []
    for k, (op, ta, tb) in enumerate(plan):
        codigo = f"E{k + 1:02d}"
        for _ in range(5000):
            if op == "suma":
                a, b, c, d = (frozenset(rng.sample(todos, t)) for t in (ta, tb, ta, tb))
                m = [[a, b, a | b], [c, d, c | d], [a | c, b | d, a | b | c | d]]
            else:
                m = []
                for _ in range(3):
                    x = frozenset(rng.sample(todos, ta))
                    if op == "resta":
                        y = frozenset(rng.sample(sorted(x), min(tb, ta - 1)))
                    else:
                        comunes = rng.sample(sorted(x), max(1, min(tb - 1, ta - 1 if op == "diferencia" else ta)))
                        y = frozenset(comunes + rng.sample([t for t in todos if t not in x], tb - len(comunes)))
                    m.append([x, y, OPS[op](x, y)])
            celdas = [c for fila in m for c in fila]
            if any(not c for c in celdas) or len(set(celdas)) < 8 or len(m[2][2]) < (1 if k < 4 else 2):
                continue
            if predicciones(m) != {frozenset(m[2][2])}:
                continue
            tercera = sorted(set(m[2][0]) | set(m[2][1]) | set(m[1][2]))
            candidatos = [t for t in tercera] + [t for t in todos if t not in tercera]
            rng.shuffle(candidatos)
            toggles = None
            for trio in itertools.combinations(candidatos[:7], 3):
                ops = [frozenset(set(m[2][2]) ^ set(sub)) for r in range(4) for sub in itertools.combinations(trio, r)]
                if all(ops) and len(set(ops)) == 8:
                    toggles = trio
                    break
            if toggles:
                break
        else:
            raise SystemExit(f"{codigo}: no se encontró una matriz con respuesta única")
        celdas_a = [{"trazos": sorted(c)} for c in celdas]
        it.append(trazos_item(codigo, celdas_a, m[2][2], toggles, REGLAS_E[op], rng, pos[k]))
    return it


def trazos_item(codigo, celdas, respuesta, toggles, regla, rng, pos):
    ids = Ids(codigo)
    correcta = {"trazos": sorted(respuesta)}
    distractores = [{"trazos": sorted(set(respuesta) ^ set(sub))} for r in range(1, 4) for sub in itertools.combinations(toggles, r)]
    orden = ordenar(rng, correcta, distractores, pos)
    return ({"celdas": [celda(ids, c) for c in celdas[:-1]] + [None], "opciones": [celda(ids, o) for o in orden]},
            pos, {"regla": regla, "opciones": [describir(o) for o in orden]})


# ====== Serie A: patrones continuos ======

ANCHO, ALTO, HUECO = 300, 200, 70
EXT = (-200, -200, 500, 400)


def rango(a, b, paso):
    x = a
    while x <= b + 1e-9:
        yield x
        x += paso


def caja(p):
    t = p[0]
    if t == "linea":
        _, x1, y1, x2, y2, _g = p
        return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
    if t == "circulo":
        _, cx, cy, r, _f, _g = p
        return cx - r, cy - r, cx + r, cy + r
    if t == "rect":
        _, x, y, w, h, _f = p
        return x, y, x + w, y + h
    xs = [x for x, _ in p[1]]
    ys = [y for _, y in p[1]]
    return min(xs), min(ys), max(xs), max(ys)


def svg_prim(p):
    t = p[0]
    if t == "linea":
        _, x1, y1, x2, y2, g = p
        return f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{TINTA}" stroke-width="{n(g)}"/>'
    if t == "circulo":
        _, cx, cy, r, f, g = p
        return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{TINTA if f else "none"}"' + (f' stroke="{TINTA}" stroke-width="{n(g)}"' if g else "") + "/>"
    if t == "rect":
        _, x, y, w, h, f = p
        return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{TINTA if f else "none"}"' + ("" if f else f' stroke="{TINTA}" stroke-width="2.5"') + "/>"
    _, pts, cerrado, g = p
    etiqueta = "polygon" if cerrado else "polyline"
    return f'<{etiqueta} points="{pts_txt(pts)}" fill="none" stroke="{TINTA}" stroke-width="{n(g)}" stroke-linejoin="round"/>'


def recortar(prims, x0, y0, x1, y1):
    """Solo las primitivas que tocan la región; las líneas largas se recortan para no inflar el SVG."""
    out = []
    for p in prims:
        a, b, c, d = caja(p)
        if c < x0 or a > x1 or d < y0 or b > y1:
            continue
        if p[0] == "poli" and not p[2]:
            pts = p[1]
            dentro = [k for k, (x, y) in enumerate(pts) if x0 - 30 <= x <= x1 + 30 and y0 - 30 <= y <= y1 + 30]
            if not dentro:
                continue
            p = ("poli", pts[max(0, dentro[0] - 1): dentro[-1] + 2], False, p[3])
        elif p[0] == "linea":
            p = recortar_linea(p, x0 - 5, y0 - 5, x1 + 5, y1 + 5)
            if p is None:
                continue
        out.append(p)
    return out


def recortar_linea(p, x0, y0, x1, y1):
    _, ax, ay, bx, by, g = p
    t0, t1, dx, dy = 0.0, 1.0, bx - ax, by - ay
    for pp, q in ((-dx, ax - x0), (dx, x1 - ax), (-dy, ay - y0), (dy, y1 - ay)):
        if pp == 0:
            if q < 0:
                return None
        else:
            r = q / pp
            if pp < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
    if t0 > t1:
        return None
    return ("linea", ax + t0 * dx, ay + t0 * dy, ax + t1 * dx, ay + t1 * dy, g)


def p_rayas(angulo, sep, g=3):
    prims = []
    a = math.radians(angulo)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    for t in rango(-700, 700, sep):
        cx, cy = 150 + nx * t, 100 + ny * t
        prims.append(("linea", cx - ux * 800, cy - uy * 800, cx + ux * 800, cy + uy * 800, g))
    return prims


def p_zigzag(periodo=24, amp=7, sep=24, g=2.5, vertical=False):
    prims = []
    for y in rango(EXT[1], EXT[3], sep):
        pts = [(x, y + (amp if k % 2 else -amp)) for k, x in enumerate(rango(EXT[0], EXT[2], periodo / 2))]
        if vertical:
            pts = [(y, x) for x, y in pts]
        prims.append(("poli", pts, False, g))
    return prims


def p_ondas(periodo=40, amp=6, sep=20, g=2.5):
    prims = []
    for y in rango(EXT[1], EXT[3], sep):
        pts = [(x, y + amp * math.sin(2 * math.pi * x / periodo)) for x in rango(EXT[0], EXT[2], 3)]
        prims.append(("poli", pts, False, g))
    return prims


def p_ladrillos(w=40, h=20, g=2.5):
    prims = []
    for k, y in enumerate(rango(EXT[1], EXT[3], h)):
        prims.append(("linea", EXT[0], y, EXT[2], y, g))
        desfase = (w / 2) if k % 2 else 0
        for x in rango(EXT[0] + desfase, EXT[2], w):
            prims.append(("linea", x, y, x, y + h, g))
    return prims


def p_puntos(sep=20, r=4, hexagonal=True):
    prims = []
    for k, y in enumerate(rango(EXT[1], EXT[3], sep * (0.87 if hexagonal else 1))):
        desfase = sep / 2 if (hexagonal and k % 2) else 0
        for x in rango(EXT[0] + desfase, EXT[2], sep):
            prims.append(("circulo", x, y, r, True, 0))
    return prims


def p_anillos_sueltos(sep=20):
    prims = []
    for k, y in enumerate(rango(EXT[1], EXT[3], sep * 0.87)):
        for x in rango(EXT[0] + (sep / 2 if k % 2 else 0), EXT[2], sep):
            prims.append(("circulo", x, y, 5, False, 2))
    return prims


def p_filas(sep=24, cual=("circulo", "cuadrado")):
    prims = []
    for k, y in enumerate(rango(EXT[1], EXT[3], sep)):
        tipo = cual[k % len(cual)]
        for x in rango(EXT[0], EXT[2], sep):
            if tipo == "circulo":
                prims.append(("circulo", x, y, 6, False, 2.5))
            else:
                prims.append(("rect", x - 6, y - 6, 12, 12, False))
    return prims


def p_rombos(paso=40, g=2.5):
    prims = []
    for k in rango(-800, 800, paso):
        prims.append(("linea", EXT[0], EXT[0] + k, EXT[2], EXT[2] + k, g))
        prims.append(("linea", EXT[0], -EXT[0] + k, EXT[2], -EXT[2] + k, g))
    return prims


def p_cuadricula(paso=24, g=2.5):
    return p_rayas(0, paso, g) + p_rayas(90, paso, g)


def p_anillos(cx=150, cy=100, sep=14, g=2.5):
    return [("circulo", cx, cy, r, False, g) for r in rango(sep, 420, sep)]


def secuencia(inicio, paso0, crece, desde, hasta):
    """Posiciones con separación creciente: la separación aumenta en 'crece' en cada línea."""
    pos, x, s = [], inicio, paso0
    while x <= hasta:
        pos.append(x)
        x += s
        s += crece
    x, s = inicio, paso0
    while x >= desde:
        s = max(3, s - crece)
        x -= s
        pos.append(x)
    return sorted(pos)


def p_lineas_gradiente(g=2.5):
    return [("linea", EXT[0], y, EXT[2], y, g) for y in secuencia(0, 5, 1.6, -60, 420)]


def p_puntos_crecientes(sep=24, forma="circulo"):
    prims = []
    for y in rango(EXT[1] + 4, EXT[3], sep):
        for x in rango(EXT[0] + 4, EXT[2], sep):
            r = min(10.5, max(1.2, 1.5 + 0.024 * x))
            if forma == "circulo":
                prims.append(("circulo", x, y, r, True, 0))
            else:
                prims.append(("rect", x - r, y - r, 2 * r, 2 * r, True))
    return prims


def p_cruces(sep=22):
    prims = []
    for y in rango(EXT[1], EXT[3], sep):
        for x in rango(EXT[0], EXT[2], sep):
            prims += [("linea", x - 5, y, x + 5, y, 2.5), ("linea", x, y - 5, x, y + 5, 2.5)]
    return prims


def p_rayos(ox=30, oy=215, paso=7, g=2.5):
    prims = []
    for ang in rango(-178, 178, paso):
        a = math.radians(ang)
        prims.append(("linea", ox, oy, ox + 900 * math.cos(a), oy + 900 * math.sin(a), g))
    return prims


def p_rejilla_gradiente(verticales=True, horizontales=True, g=2.5):
    prims = []
    if verticales:
        xs = []
        x, s = 320.0, 5.0
        while x > -400:
            xs.append(x)
            x -= s
            s = min(40, s + 1.5)
        prims += [("linea", x, EXT[1], x, EXT[3], g) for x in xs]
    if horizontales:
        ys = []
        y, s = 230.0, 5.0
        while y > -400:
            ys.append(y)
            y -= s
            s = min(40, s + 1.5)
        prims += [("linea", EXT[0], y, EXT[2], y, g) for y in ys]
    return prims


def p_figuras_grandes(banda=True, arco=True):
    prims = p_puntos(sep=26, r=2.2, hexagonal=False)
    if arco:
        prims.append(("circulo", 115, 100, 78, False, 4.5))
    if banda:
        prims.append(("linea", -60, 240, 360, -40, 11))
    return prims


def interseccion_figuras():
    """Punto donde la banda cruza el círculo grande del lado derecho (centro del hueco de A12)."""
    mejor = None
    for k in range(0, 3600):
        a = math.radians(k / 10)
        x, y = 115 + 78 * math.cos(a), 100 + 78 * math.sin(a)
        yb = 240 + (x + 60) * (-280 / 420)
        if x > 115 and (mejor is None or abs(y - yb) < mejor[0]):
            mejor = (abs(y - yb), x, y)
    return mejor[1], mejor[2]


def pieza(prims, hx, hy, transformacion=None):
    """Contenido de una opción: la región del hueco (o la indicada) escalada a 100 x 100."""
    rx, ry = hx, hy
    t = ""
    if transformacion:
        tipo = transformacion[0]
        cx, cy = hx + HUECO / 2, hy + HUECO / 2
        if tipo == "mover":
            rx, ry = hx + transformacion[1], hy + transformacion[2]
        elif tipo == "girar":
            t = f" rotate({transformacion[1]} {n(cx)} {n(cy)})"
        elif tipo == "espejo_h":
            t = f" matrix(-1 0 0 1 {n(2 * cx)} 0)"
        elif tipo == "espejo_v":
            t = f" matrix(1 0 0 -1 0 {n(2 * cy)})"
    if transformacion and transformacion[0] == "vacio":
        return ""
    k = 100 / HUECO
    dentro = recortar(prims, rx - 12, ry - 12, rx + HUECO + 12, ry + HUECO + 12)
    return f'<g transform="scale({round(k, 4)}) translate({n(-rx)} {n(-ry)}){t}">' + "".join(svg_prim(p) for p in dentro) + "</g>"


def lienzo(prims, hx, hy):
    dentro = recortar(prims, -10, -10, ANCHO + 10, ALTO + 10)
    return ("".join(svg_prim(p) for p in dentro) +
            f'<rect x="{n(hx)}" y="{n(hy)}" width="{HUECO}" height="{HUECO}" fill="#fff" stroke="{TINTA}" stroke-width="2.5"/>')


def textura(codigo, prims, hx, hy, distractores, regla, rng, pos):
    """distractores: [(descripción, primitivas, transformación)]; la correcta es la región del hueco."""
    correcta = ("continúa el patrón sin cortes", pieza(prims, hx, hy))
    otros = [(d, pieza(p if p is not None else prims, hx, hy, t)) for d, p, t in distractores]
    if len(otros) != 5:
        raise SystemExit(f"{codigo}: se necesitan 5 distractores")
    orden = ordenar(rng, correcta, otros, pos)
    return ({"lienzo": lienzo(prims, hx, hy), "vista": f"0 0 {ANCHO} {ALTO}", "opciones": [o[1] for o in orden]},
            pos, {"regla": regla, "opciones": [o[0] for o in orden]})


def serie_a(rng, pos):
    it = []
    zz = p_zigzag()
    it.append(textura("A01", zz, 170, 64, [
        ("vacía", None, ("vacio",)), ("zigzag en vertical", None, ("girar", 90)), ("puntos", p_puntos(), None),
        ("rayas diagonales", p_rayas(45, 16), None), ("ladrillos", p_ladrillos(), None)],
        "Líneas en zigzag horizontales y parejas.", rng, pos[0]))
    lad = p_ladrillos()
    it.append(textura("A02", lad, 58, 86, [
        ("ladrillos en vertical", None, ("girar", 90)), ("ladrillos más chicos", p_ladrillos(24, 12), None),
        ("zigzag", zz, None), ("puntos", p_puntos(), None), ("vacía", None, ("vacio",))],
        "Muro de ladrillos: cada hilera tiene las juntas a la mitad de los ladrillos de la hilera de arriba.", rng, pos[1]))
    pts = p_puntos(sep=20, r=4)
    it.append(textura("A03", pts, 140, 58, [
        ("puntos en cuadrícula (uno debajo de otro)", p_puntos(sep=20, r=4, hexagonal=False), None), ("puntos más grandes", p_puntos(sep=20, r=7), None),
        ("círculos huecos", p_anillos_sueltos(), None), ("rayas horizontales", p_rayas(0, 17), None), ("cruces", p_cruces(), None)],
        "Puntos iguales en hileras alternadas: cada hilera está corrida medio espacio respecto a la de arriba.", rng, pos[2]))
    on = p_ondas()
    it.append(textura("A04", on, 100, 76, [
        ("zigzag de picos", p_zigzag(periodo=40, amp=6, sep=20), None), ("ondas el doble de cerradas", p_ondas(periodo=20), None),
        ("ondas en vertical", None, ("girar", 90)), ("rayas rectas", p_rayas(0, 20), None), ("vacía", None, ("vacio",))],
        "Líneas onduladas suaves, todas iguales y paralelas.", rng, pos[3]))
    fi = p_filas()
    it.append(textura("A05", fi, 190, 50, [
        ("hileras intercambiadas (cuadros donde van círculos)", None, ("mover", 0, 24)), ("solo círculos", p_filas(cual=("circulo",)), None),
        ("columnas en lugar de hileras", None, ("girar", 90)), ("solo cuadros", p_filas(cual=("cuadrado",)), None),
        ("figuras corridas medio espacio", None, ("mover", 12, 0))],
        "Hileras que alternan: una de círculos, una de cuadros; las figuras quedan una debajo de otra.", rng, pos[4]))
    ro = p_rombos()
    it.append(textura("A06", ro, 112, 62, [
        ("cuadrícula recta", p_cuadricula(28), None), ("rombos más chicos", p_rombos(24), None),
        ("rombos corridos medio rombo", None, ("mover", 20, 0)), ("puntos", p_puntos(), None), ("vacía", None, ("vacio",))],
        "Red de líneas diagonales cruzadas que forman rombos.", rng, pos[5]))
    an = p_anillos()
    it.append(textura("A07", an, 204, 60, [
        ("arcos curvados al revés", None, ("espejo_h",)), ("arcos girados", None, ("girar", 90)),
        ("arcos de otra parte del dibujo", None, ("mover", -60, -45)), ("rayas diagonales rectas", p_rayas(45, 14), None), ("vacía", None, ("vacio",))],
        "Círculos uno dentro de otro con el mismo centro; el hueco cae sobre la parte derecha de los anillos.", rng, pos[6]))
    lg = p_lineas_gradiente()
    it.append(textura("A08", lg, 115, 96, [
        ("líneas más juntas (de más arriba)", None, ("mover", 0, -82)), ("líneas más separadas (de más abajo)", None, ("mover", 0, 110)),
        ("líneas en vertical", None, ("girar", 90)), ("ondas", p_ondas(sep=20), None), ("vacía", None, ("vacio",))],
        "Líneas horizontales que se separan cada vez más de arriba hacia abajo.", rng, pos[7]))
    pc = p_puntos_crecientes()
    it.append(textura("A09", pc, 118, 62, [
        ("puntos más chicos (de más a la izquierda)", None, ("mover", -110, 0)), ("puntos más grandes (de más a la derecha)", None, ("mover", 150, 0)),
        ("cuadros que crecen", p_puntos_crecientes(forma="cuadrado"), None), ("cruces", p_cruces(), None), ("vacía", None, ("vacio",))],
        "Puntos en cuadrícula que crecen de izquierda a derecha.", rng, pos[8]))
    ra = p_rayos()
    it.append(textura("A10", ra, 150, 36, [
        ("rayos inclinados al revés", None, ("espejo_h",)), ("rayos cerca del centro", None, ("mover", -110, 95)),
        ("rayos girados", None, ("girar", 90)), ("ondas", p_ondas(), None), ("vacía", None, ("vacio",))],
        "Rayos que salen de un punto de la esquina de abajo a la izquierda.", rng, pos[9]))
    rg = p_rejilla_gradiente()
    it.append(textura("A11", rg, 150, 78, [
        ("líneas más separadas (de más arriba a la izquierda)", None, ("mover", -140, -70)),
        ("líneas más juntas (de más abajo a la derecha)", None, ("mover", 110, 70)),
        ("solo líneas verticales", p_rejilla_gradiente(horizontales=False), None), ("solo líneas horizontales", p_rejilla_gradiente(verticales=False), None),
        ("vacía", None, ("vacio",))],
        "Rejilla: las líneas verticales se juntan hacia la derecha y las horizontales se juntan hacia abajo.", rng, pos[10]))
    fg = p_figuras_grandes()
    x, y = interseccion_figuras()
    hx, hy = round(x - HUECO / 2), round(y - HUECO / 2)
    it.append(textura("A12", fg, hx, hy, [
        ("solo el borde del círculo, sin la banda", p_figuras_grandes(banda=False), None), ("solo la banda, sin el borde del círculo", p_figuras_grandes(arco=False), None),
        ("círculo y banda volteados", None, ("espejo_h",)), ("círculo y banda girados", None, ("girar", 90)),
        ("cruce de otra parte del dibujo", None, ("mover", -118, -40))],
        "Un círculo grande y una banda diagonal gruesa sobre un fondo de puntos; el hueco cae donde la banda cruza el borde del círculo.", rng, pos[11]))
    return it


# ====== Ejemplos (no cuentan) ======

def ejemplos(rng):
    ej = {}
    ra = p_rayas(0, 18)
    item, k, _ = textura("EjA", ra, 120, 64, [
        ("vacía", None, ("vacio",)), ("rayas en vertical", None, ("girar", 90)), ("puntos", p_puntos(), None),
        ("cuadrícula", p_cuadricula(24), None), ("zigzag", p_zigzag(), None)], "", rng, 2)
    ej["A"] = {**item, "key": k}
    item, k, _ = analogia("EjB", {"forma": "circulo", "tam": "S"}, cambia(tam="L"), cambia(forma="cuadrado"),
                          [("tam", ["S"]), ("forma", ["circulo", "triangulo"])], "", rng, 4)
    ej["B"] = {**item, "key": k}
    item, k, _ = tabla("EjC", lambda i, j: {"forma": "circulo", "n": j + 1, "relleno": "negro", "tam": "L", "varias": True},
                       [("n", [2]), ("forma", ["cuadrado"]), ("relleno", ["blanco"])], "", rng, 5)
    ej["C"] = {**item, "key": k}
    item, k, _ = tabla("EjD", lambda i, j: {"forma": ["circulo", "cuadrado", "triangulo"][L1[i][j]], "tam": "L"},
                       [("forma", ["triangulo"]), ("relleno", ["negro"]), ("tam", ["S"])], "", rng, 1)
    ej["D"] = {**item, "key": k}
    ids = Ids("EjE")
    fila = [{"trazos": ["horiz"]}, {"trazos": ["vert"]}, {"trazos": ["horiz", "vert"]}]
    celdas = fila + [{"trazos": ["arriba"]}, {"trazos": ["abajo"]}, {"trazos": ["abajo", "arriba"]},
                     {"trazos": ["izq"]}, {"trazos": ["der"]}]
    correcta = {"trazos": ["der", "izq"]}
    otros = [{"trazos": ["izq"]}, {"trazos": ["der"]}, {"trazos": ["der", "horiz", "izq"]}, {"trazos": ["der", "izq", "vert"]},
             {"trazos": ["horiz", "vert"]}, {"trazos": ["arriba", "der", "izq"]}, {"trazos": ["abajo", "arriba"]}]
    orden = otros[:6] + [correcta] + otros[6:]
    ej["E"] = {"celdas": [celda(ids, c) for c in celdas] + [None], "opciones": [celda(ids, o) for o in orden], "key": 6}
    return ej


def generar():
    rng = random.Random(SEMILLA)
    pos6 = posiciones(rng, 24, 6)
    pos8 = posiciones(rng, 36, 8)
    series = {
        "A": serie_a(rng, pos6[:12]),
        "B": serie_b(rng, pos6[12:]),
        "C": serie_c(rng, pos8[:12]),
        "D": serie_d(rng, pos8[12:24]),
        "E": serie_e(rng, pos8[24:]),
    }
    reactivos = {s: [x[0] for x in v] for s, v in series.items()}
    clave = {s: [x[1] for x in v] for s, v in series.items()}
    desc = {s: [x[2] for x in v] for s, v in series.items()}
    return reactivos, clave, desc, ejemplos(rng)


def escribir(ruta, datos):
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main():
    reactivos, clave, desc, ej = generar()
    datos = CARPETA / "datos"
    escribir(datos / "reactivos.json", reactivos)
    escribir(datos / "clave.json", clave)
    escribir(datos / "descripciones.json", desc)
    escribir(datos / "ejemplos.json", ej)
    total = sum(len(v) for v in reactivos.values())
    print(f"Generados {total} reactivos en {', '.join(reactivos)} y 5 ejemplos")


if __name__ == "__main__":
    main()
