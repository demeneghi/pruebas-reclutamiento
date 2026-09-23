# Pruebas de reclutamiento de Amador Russell

Pruebas psicométricas digitales para aplicar en tablet o teléfono. Cada prueba es un solo archivo HTML que funciona sin conexión y genera al final un prompt para calificar con IA.

## Pruebas disponibles

| Prueba | Archivo |
|---|---|
| Razonamiento General, Forma B | `pruebas/razonamiento-forma-b/src/prueba.html` |

## Uso rápido

1. Abre el HTML en Chrome o Safari, no dentro de Telegram, WhatsApp u otra app.
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

## Aviso

El repositorio contiene claves de respuestas. Debe ser privado y nunca debe contener datos reales de candidatos.
