# Pruebas de reclutamiento de Amador Russell

Pruebas psicométricas digitales para aplicar en tablet o teléfono. Cada prueba es un solo archivo HTML que funciona sin conexión y genera al final un prompt para calificar con IA.

## Pruebas disponibles

| Prueba | En línea | Archivo |
|---|---|---|
| Razonamiento General, Forma B | https://demeneghi.github.io/pruebas-reclutamiento/razonamiento-forma-b/ | `pruebas/razonamiento-forma-b/src/prueba.html` |
| Razonamiento con Figuras, Forma A | https://demeneghi.github.io/pruebas-reclutamiento/razonamiento-figuras/ | `pruebas/razonamiento-figuras/src/prueba.html` |

La raíz https://demeneghi.github.io/pruebas-reclutamiento/ muestra el menú de pruebas. Si en ese dispositivo hay una aplicación a medias, la reabre sola.

## Uso rápido

1. Abre la raíz del sitio en Chrome o Safari, no dentro de Telegram, WhatsApp u otra app. Usa siempre el mismo enlace en cada dispositivo: el historial se guarda por sitio.
2. Captura los datos del candidato una sola vez. Desde ese momento su nombre aparece arriba del menú.
3. Elige la prueba y entrega el dispositivo. La prueba empieza en la bienvenida del candidato.
4. Al terminar, mantén presionado "volver al menú de pruebas" y elige la siguiente prueba.
5. En el menú, mantén presionado "ver resultados y prompt": anota incidencias por prueba y copia un solo prompt con todas las pruebas del candidato.
6. Mantén presionado "terminar con este candidato": sus resultados quedan en "Candidatos anteriores" y el menú queda listo para el siguiente.
7. Para salir de una prueba a medias, mantén presionado 3 s el botón "Salir" y elige "Volver al menú de pruebas". La aplicación queda cancelada y se puede aplicar de nuevo.

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
