# Pruebas de reclutamiento de Amador Russell

Pruebas psicométricas digitales para aplicar en tablet o teléfono. Cada prueba es un solo archivo HTML que funciona sin conexión y genera al final un prompt para calificar con IA.

## Pruebas disponibles

| Prueba | En línea | Archivo |
|---|---|---|
| Razonamiento General, Forma B | https://demeneghi.github.io/pruebas-reclutamiento/razonamiento-forma-b/ | `pruebas/razonamiento-forma-b/src/prueba.html` |

La raíz https://demeneghi.github.io/pruebas-reclutamiento/ muestra el menú de pruebas. Si en ese dispositivo hay una aplicación a medias, la reabre sola.

## Uso rápido

1. Abre la raíz del sitio en Chrome o Safari, no dentro de Telegram, WhatsApp u otra app. Usa siempre el mismo enlace en cada dispositivo: el historial se guarda por sitio.
2. El aplicador elige la prueba, captura los datos del candidato y el tipo de puesto, y entrega el dispositivo.
3. Al terminar, el aplicador mantiene presionado el botón de resultados y copia el prompt.
4. Para un candidato nuevo, en el menú mantén presionado "Preparar para un candidato nuevo": lo pendiente se archiva en el historial y todas las pruebas abren en la pantalla de captura.
5. Para salir de una prueba a medias, mantén presionado 3 s el título de la parte y elige "Volver al menú de pruebas". La aplicación queda cancelada en el historial.

## Estructura

| Ruta | Contenido |
|---|---|
| `.claude/rules/` | Reglas que Claude Code respeta en todas las pruebas |
| `pruebas/<prueba>/src/` | `config.js` con lo propio de la prueba y `prueba.html` generado |
| `pruebas/<prueba>/datos/` | Reactivos y clave en JSON, fuente de verdad |
| `pruebas/<prueba>/fuentes/` | Material original |
| `pruebas/<prueba>/docs/` | Decisiones, correcciones y pendientes |
| `pruebas/<prueba>/tests/` | Pruebas de extremo a extremo con Playwright |
| `motor/` | Plantilla, estilos y lógica comunes a todas las pruebas |
| `herramientas/construir.py` | Genera cada `prueba.html`; `--verificar` confirma que está al día |
| `marca/` | Logotipo original, SVG vectorizado y script que lo genera |
| `sitio/` | Menú de pruebas en la raíz de GitHub Pages y su prueba automatizada |
| `.github/workflows/pages.yml` | Publicación en GitHub Pages |
| `.github/workflows/pruebas.yml` | Construcción y pruebas automatizadas en cada PR |

## Publicación

Cada push a `main` que cambie una aplicación publica en GitHub Pages solo `pruebas/<prueba>/src/prueba.html`, como `<prueba>/index.html`. No se publican `datos/`, `fuentes/` ni `docs/`. En Settings, Pages, el origen debe ser GitHub Actions.

## Aviso

El repositorio contiene claves de respuestas. Debe ser privado y nunca debe contener datos reales de candidatos. El sitio de Pages es público aunque el repositorio sea privado, y la clave va ofuscada dentro de la aplicación.
