# Pruebas de reclutamiento de Amador Russell

## Qué es este repositorio

Pruebas psicométricas digitales para el reclutamiento de Amador Russell SPR de RL, empresa agrícola productora de piña MD2 en Veracruz, México. Cada prueba es un HTML autocontenido que se aplica en tablet o teléfono y al final genera un prompt para que una IA califique e interprete.

Dueño: Gonzalo Amador Demeneghi (Chalo).

## Reglas

Las reglas del repositorio están en `.claude/rules/` y aplican a todas las pruebas, actuales y futuras. Las de `comunicacion-y-formato.md`, `integridad-psicometrica.md` y `nueva-prueba.md` aplican siempre; las demás se cargan al trabajar en `src/`, `datos/` o `tests/` de cualquier prueba. Si una petición contradice una regla, señálalo antes de actuar.

## Pruebas

| Carpeta | Prueba | Estado |
|---|---|---|
| `pruebas/razonamiento-forma-b/` | Razonamiento General, Forma B (tipo Terman-Merrill, 10 series, 165 reactivos) | En uso; publicada como artefacto privado de Claude |

Cada carpeta tiene su propio `CLAUDE.md` con el contexto específico.

## Comandos

```bash
pip install playwright && python -m playwright install chromium
python pruebas/razonamiento-forma-b/tests/test_flujo_completo.py
python pruebas/razonamiento-forma-b/tests/test_persistencia.py
```
