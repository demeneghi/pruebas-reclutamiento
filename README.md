# Pruebas de reclutamiento de Amador Russell

Pruebas psicométricas digitales para aplicar en tablet o teléfono. Cada prueba es un solo archivo HTML que funciona sin conexión y genera al final un prompt para calificar con IA.

## Pruebas disponibles

| Prueba | En línea | Archivo |
|---|---|---|
| Razonamiento General, Forma B | https://demeneghi.github.io/pruebas-reclutamiento/razonamiento-forma-b/ | `pruebas/razonamiento-forma-b/src/prueba.html` |

La raíz https://demeneghi.github.io/pruebas-reclutamiento/ redirige a la prueba.

## Uso rápido

1. Abre el enlace de la prueba en Chrome o Safari, no dentro de Telegram, WhatsApp u otra app. Usa siempre el mismo enlace en cada dispositivo: el historial se guarda por sitio.
2. El aplicador captura los datos del candidato y el tipo de puesto, y entrega el dispositivo.
3. Al terminar, el aplicador mantiene presionado el botón de resultados y copia el prompt.

## Estructura

| Ruta | Contenido |
|---|---|
| `.claude/rules/` | Reglas que Claude Code respeta en todas las pruebas |
| `pruebas/<prueba>/src/` | Aplicación, fuente de verdad |
| `pruebas/<prueba>/datos/` | Reactivos y clave en JSON |
| `pruebas/<prueba>/fuentes/` | Material original |
| `pruebas/<prueba>/docs/` | Decisiones, correcciones y pendientes |
| `pruebas/<prueba>/tests/` | Pruebas de extremo a extremo con Playwright |
| `sitio/` | Página raíz de GitHub Pages |
| `.github/workflows/pages.yml` | Publicación en GitHub Pages |

## Publicación

Cada push a `main` que cambie una aplicación publica en GitHub Pages solo `pruebas/<prueba>/src/prueba.html`, como `<prueba>/index.html`. No se publican `datos/`, `fuentes/` ni `docs/`. En Settings, Pages, el origen debe ser GitHub Actions.

## Aviso

El repositorio contiene claves de respuestas. Debe ser privado y nunca debe contener datos reales de candidatos. El sitio de Pages es público aunque el repositorio sea privado, y la clave va ofuscada dentro de la aplicación.
