# Pruebas de reclutamiento de Amador Russell

## Qué es este repositorio

Pruebas psicométricas digitales para el reclutamiento de Amador Russell SPR de RL, empresa agrícola productora de piña MD2 en Veracruz, México. Cada prueba es un HTML autocontenido que se aplica en tablet o teléfono y al final genera un prompt para que una IA califique e interprete.

Dueño: Gonzalo Amador Demeneghi (Chalo).

## Reglas

Las reglas del repositorio están en `.claude/rules/` y aplican a todas las pruebas, actuales y futuras. Las de `comunicacion-y-formato.md`, `integridad-psicometrica.md` y `nueva-prueba.md` aplican siempre; las demás se cargan al trabajar en `src/`, `datos/` o `tests/` de cualquier prueba. Si una petición contradice una regla, señálalo antes de actuar.

## Pruebas

| Carpeta | Prueba | Estado |
|---|---|---|
| `pruebas/razonamiento-forma-b/` | Razonamiento General, Forma B (tipo Terman-Merrill, 10 series, 165 reactivos) | En uso; publicada en GitHub Pages (https://demeneghi.github.io/pruebas-reclutamiento/razonamiento-forma-b/) y como artefacto privado de Claude |

Cada carpeta tiene su propio `CLAUDE.md` con el contexto específico.

## Marca

`marca/` guarda el logotipo original (`logo-amador-russell.png`), el script que lo vectoriza en piezas animables (`vectorizar_logo.py`, requiere pillow, numpy, scipy y potrace) y el SVG resultante. Si cambia el logotipo, regenera el SVG y cópialo en la constante `LOGO` de cada `src/prueba.html`.

## Publicación

`.github/workflows/pages.yml` publica en GitHub Pages cada `pruebas/<prueba>/src/prueba.html` como `<prueba>/index.html`, más `sitio/index.html` en la raíz. Nada más del repositorio llega al sitio.

`sitio/index.html` es el menú de pruebas: una tarjeta por prueba, escrita a mano. Si el dispositivo tiene una aplicación en curso, la raíz la reabre sola. Cada prueba define `CARPETA` para ofrecer "Cambiar de prueba" en la pantalla del aplicador cuando se sirve desde Pages.

## Comandos

```bash
pip install playwright && python -m playwright install chromium
python pruebas/razonamiento-forma-b/tests/test_flujo_completo.py
python pruebas/razonamiento-forma-b/tests/test_persistencia.py
python pruebas/razonamiento-forma-b/tests/test_indicadores.py
python sitio/tests/test_selector.py
```
