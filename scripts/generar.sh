#!/usr/bin/env bash
# Regenera las imágenes del README y el propio README. Necesita: ARCHIVO_TTF, PW (playwright-core), THREE_DIR, RETRATO_BIN,
# JOELSPHERE (public de joelsphere) e IDENTIDAD (identidad de INSIDEEBB). GL elige la gráfica de Chromium.
set -euo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
A="t=6&ay=0.13&ax=0.03&cam=3.9&onda=0.35"; O="$A&dpr=0.95&b=0.8"; C="$A&dpr=1.15&b=1.1&claro=1"
(cd scripts/retrato
  node render.cjs "$T/oscuro-e" 72 380 360 2 "$O&dy=0.12"; node render.cjs "$T/oscuro-m" 72 400 290 2 "$O&dy=0.2"
  node render.cjs "$T/claro-e" 72 380 360 2 "$C&dy=0.12"; node render.cjs "$T/claro-m" 72 400 290 2 "$C&dy=0.2")
python3 scripts/hero.py "$T"
python3 scripts/tarjetas.py
python3 scripts/readme.py
