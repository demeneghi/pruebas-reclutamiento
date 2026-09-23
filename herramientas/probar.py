"""Verifica la construcción y corre en paralelo todas las pruebas de extremo a extremo.

Uso:
    python herramientas/probar.py
"""
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def correr(ruta):
    inicio = time.time()
    r = subprocess.run([sys.executable, str(ruta)], cwd=RAIZ, capture_output=True, text=True, timeout=600)
    return ruta.relative_to(RAIZ).as_posix(), r.returncode, time.time() - inicio, (r.stdout + r.stderr).strip()


def main():
    construccion = subprocess.run([sys.executable, str(RAIZ / "herramientas" / "construir.py"), "--verificar"], cwd=RAIZ)
    if construccion.returncode:
        sys.exit(1)
    pruebas = sorted(RAIZ.glob("pruebas/*/tests/test_*.py")) + sorted(RAIZ.glob("sitio/tests/test_*.py"))
    with ThreadPoolExecutor(max_workers=len(pruebas)) as grupo:
        resultados = list(grupo.map(correr, pruebas))
    fallas = 0
    for nombre, codigo, segundos, salida in resultados:
        ultima = salida.splitlines()[-1] if salida else ""
        print(f"{'OK   ' if codigo == 0 else 'FALLA'} {segundos:5.1f} s  {nombre}  {ultima if codigo == 0 else ''}")
        if codigo:
            fallas += 1
            print("      " + salida.replace("\n", "\n      "))
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
