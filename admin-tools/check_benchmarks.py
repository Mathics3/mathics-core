#!/usr/bin/env python3
"""
Herramienta CLI para detectar regresiones de rendimiento comparando dos archivos JSON
generados por pytest-benchmark (--benchmark-json=output.json).

Uso:
  # Comparar dos archivos locales
  python check_benchmarks.py output_master.json output_new.json

  # Comparar contra la rama gh-pages (descarga automática)
  python check_benchmarks.py output.json --threshold=1.5

  # Cambiar umbral de regresión (por defecto 1.5 = 150% más lento)
  python check_benchmarks.py output_new.json --threshold=2.0

Salida:
  - Código de salida 0: sin regresiones significativas
  - Código de salida 1: se detectaron regresiones (con mensajes en stdout)
"""

import argparse
import json
import os
import sys
from pathlib import Path


def load_benchmarks(json_path):
    """Carga un archivo JSON de pytest-benchmark y devuelve dict {nombre: ops}."""
    with open(json_path, "r") as f:
        data = json.load(f)

    benchmarks = {}
    for b in data.get("benchmarks", []):
        name = b.get("fullname") or b.get("name")
        # Usamos OPS (operaciones por segundo) como métrica principal
        ops = b.get("stats", {}).get("ops")
        if name and ops is not None:
            benchmarks[name] = ops
    return benchmarks


def get_baseline_from_gh_pages():
    """Intenta descargar el último data.js desde gh-pages y extraer los benchmarks."""
    import requests

    url = (
        "https://raw.githubusercontent.com/Mathics3/mathics-core/gh-pages/cache/data.js"
    )
    try:
        resp = requests.get(url, timeout=10)
        print("getting resp")
        if resp.status_code == 200:
            print("resp=200")
            content = resp.text
            print("content of lenght", len(resp.text))
            # data.js tiene: var data = {...};
            # Extraemos el JSON entre "var data = " y el punto y coma final
            import re

            match = re.search(r"var data\s*=\s*({.*?});", content, re.DOTALL)
            if match:
                print("match")
                json_str = match.group(1)
                data = json.loads(json_str)
                # La estructura en data.js es ligeramente diferente:
                # { commit: {...}, date: ..., tool: 'pytest', benches: [...] }
                if "benches" in data:
                    # Convertir a formato similar al de pytest-benchmark
                    benchmarks = {}
                    for b in data["benches"]:
                        name = b.get("name")
                        value = b.get("value")  # ya es ops
                        if name and value is not None:
                            benchmarks[name] = value
                    return benchmarks
    except Exception as e:
        print(f"⚠️ No se pudo descargar baseline desde gh-pages: {e}", file=sys.stderr)
    return None


def get_baseline_from_local(baseline_path):
    """Carga un baseline desde un archivo JSON local."""
    if not Path(baseline_path).exists():
        return None
    return load_benchmarks(baseline_path)


def compare_benchmarks(current, baseline, threshold):
    """Compara dos dicts de benchmarks y devuelve lista de regresiones."""
    regressions = []
    improvements = []

    for name, cur_ops in current.items():
        base_ops = baseline.get(name)
        if base_ops is None:
            continue  # benchmark nuevo, no se puede comparar

        # Ratio = base / current; >1 significa que current es más lento
        ratio = base_ops / cur_ops if cur_ops > 0 else float("inf")
        if ratio > threshold:
            regressions.append((name, cur_ops, base_ops, ratio))
        elif ratio < 0.8:  # opcional: también reportar mejoras
            improvements.append((name, cur_ops, base_ops, ratio))

    return regressions, improvements


def main():
    parser = argparse.ArgumentParser(
        description="Detecta regresiones de rendimiento comparando dos archivos JSON de pytest-benchmark."
    )
    parser.add_argument(
        "current",
        nargs="?",
        default="output.json",
        help="Archivo JSON con los resultados actuales (por defecto: output.json)",
    )
    parser.add_argument(
        "baseline", nargs="?", help="Archivo JSON con los resultados base (opcional)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=1.5,
        help="Umbral de regresión (ratio). Por defecto 1.5 (150%% más lento)",
    )
    parser.add_argument(
        "--baseline-from-gh",
        action="store_true",
        help="Descargar baseline desde gh-pages (ignora argumento baseline)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="No mostrar detalles, solo código de salida",
    )

    args = parser.parse_args()

    # 1. Cargar resultados actuales
    try:
        current = load_benchmarks(args.current)
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {args.current}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"❌ Error al cargar {args.current}: {e}", file=sys.stderr)
        sys.exit(2)

    if not current:
        print("⚠️ No se encontraron benchmarks en el archivo actual.", file=sys.stderr)
        sys.exit(2)

    # 2. Obtener baseline
    baseline = None
    if args.baseline_from_gh:
        baseline = get_baseline_from_gh_pages()
        if baseline is None:
            print("❌ No se pudo obtener baseline desde gh-pages.", file=sys.stderr)
            sys.exit(2)
    elif args.baseline:
        try:
            baseline = get_baseline_from_local(args.baseline)
        except Exception as e:
            print(f"❌ Error al cargar baseline {args.baseline}: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        # Si no se especifica baseline, intentar descargar desde gh-pages automáticamente
        baseline = get_baseline_from_gh_pages()
        if baseline is None:
            print(
                "⚠️ No se encontró baseline local ni en gh-pages. Se usará solo el resultado actual.",
                file=sys.stderr,
            )
            sys.exit(0)

    # 3. Comparar
    regressions, improvements = compare_benchmarks(current, baseline, args.threshold)

    # 4. Mostrar resultados
    if not args.quiet:
        print(f"📊 Comparando {len(current)} benchmarks...")
        print(f"   Umbral: {args.threshold}x (regresión si ratio > {args.threshold})")
        print()

    if regressions:
        if not args.quiet:
            print("::error::⚠️ REGRESIONES DETECTADAS:")
            for name, cur, base, ratio in sorted(
                regressions, key=lambda x: x[3], reverse=True
            ):
                # Mostrar solo el nombre corto (sin ruta completa)
                short_name = name.split("::")[-1] if "::" in name else name
                print(f"  ❌ {short_name}")
                print(
                    f"     Actual: {cur:.2f} ops/sec | Base: {base:.2f} ops/sec | Ratio: {ratio:.2f}x"
                )
        sys.exit(1)
    else:
        if not args.quiet:
            print("✅ No se detectaron regresiones significativas.")
            if improvements:
                print(f"   Mejoras detectadas: {len(improvements)} benchmarks")
                # Mostrar las 3 mejores mejoras
                for name, cur, base, ratio in sorted(improvements, key=lambda x: x[3])[
                    :3
                ]:
                    short_name = name.split("::")[-1] if "::" in name else name
                    print(
                        f"  🚀 {short_name}: {cur:.2f} vs {base:.2f} (ratio {ratio:.2f})"
                    )
        sys.exit(0)


if __name__ == "__main__":
    main()
