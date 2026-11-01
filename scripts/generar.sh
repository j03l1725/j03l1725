#!/usr/bin/env bash
# Regenera todas las imágenes del README. Necesita: ARCHIVO_TTF, PW (playwright-core), THREE_DIR, RETRATO_BIN,
# JOELSPHERE (public de joelsphere) e IDENTIDAD (identidad de INSIDEEBB). GL elige la gráfica de Chromium.
set -euo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
A="t=6&ay=0.13&ax=0.03&cam=3.9&dpr=0.95&b=0.8&onda=0.35"
(cd scripts/retrato; node render.cjs "$T/e" 72 380 360 2 "$A&dy=0.12"; node render.cjs "$T/m" 72 400 290 2 "$A&dy=0.2")
python3 scripts/hero.py "$T/e" "$T/m"
python3 scripts/tarjetas.py
