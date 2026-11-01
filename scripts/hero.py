#!/usr/bin/env python3
"""Genera la cabecera del perfil como WebP animado: texto en Archivo y el retrato de joelsphere sumado encima.

Va en WebP directo y no dentro de un SVG: Firefox deja quieto un WebP animado incrustado en un SVG (medido el 2026-10-31).

Uso: ARCHIVO_TTF=<Archivo-Variable.ttf> PW=<playwright-core> python3 scripts/hero.py <cuadros escritorio> <cuadros móvil>
Los cuadros salen de scripts/retrato/render.cjs (órdenes en scripts/generar.sh).
"""
import base64, glob, io, os, subprocess, sys, tempfile
from pathlib import Path

import numpy as np
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
Q = int(os.environ.get('CALIDAD', 52)); METODO = int(os.environ.get('METODO', 4))
NOMBRE = ['Joel', 'Morales']
TITULAR = 'Lo difícil de la IA es que funcione de verdad.'
LINEAS = ['Cofundador y CTO de INSIDEEBB.', 'Youth Envoy de la UIT para las Américas.']


def fuente(peso, ancho, texto):
    f = instancer.instantiateVariableFont(TTFont(os.environ['ARCHIVO_TTF']), {'wght': peso, 'wdth': ancho})
    op = subset.Options(); op.layout_features = ['kern', 'liga']; op.notdef_outline = True
    s = subset.Subsetter(op); s.populate(text=texto); s.subset(f)
    b = io.BytesIO(); f.flavor = 'woff'; f.save(b)
    return base64.b64encode(b.getvalue()).decode()


CSS = None
def css():
    global CSS
    if CSS is None:
        n, t, c = fuente(900, 125, ''.join(NOMBRE) + ' '), fuente(600, 100, TITULAR), fuente(400, 100, ''.join(LINEAS))
        CSS = f"""<style>@font-face{{font-family:N;src:url(data:font/woff;base64,{n})}}
@font-face{{font-family:T;src:url(data:font/woff;base64,{t})}}@font-face{{font-family:C;src:url(data:font/woff;base64,{c})}}
.n{{font-family:N;fill:#fff}}.t{{font-family:T;fill:#fff}}.c{{font-family:C;fill:#A9B0BE}}</style>"""
    return CSS


def base(w, h, texto, tmp, nombre):
    """El cuadro sin retrato, de w × h píxeles finales: fondo, borde y texto, con las esquinas transparentes."""
    s = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w//2}" height="{h//2}" style="display:block;position:fixed;inset:0">{css()}
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="26" fill="#0A0C11" stroke="#2A2F3A" stroke-width="2"/>{texto}</svg>"""
    f = Path(tmp) / f'{nombre}.svg'; p = Path(tmp) / f'{nombre}.png'
    f.write_text(f'<!doctype html><html><body style="margin:0;background:transparent">{s}</body></html>')
    h_ = Path(tmp) / f'{nombre}.html'; f.rename(h_)
    subprocess.run(['node', str(REPO / 'scripts/retrato/rasterizar.cjs'), str(h_), str(p), str(w // 2), str(h // 2)], check=True)
    return np.asarray(Image.open(p).convert('RGBA'), dtype=np.float32)


def componer(bas, carpeta, x, y, rampa):
    """Suma cada cuadro del retrato sobre la base. Es la misma mezcla aditiva del sitio: el negro no añade nada, sin halo."""
    fs = sorted(glob.glob(f'{carpeta}/*.png')); salida = []
    for f in fs:
        a = np.asarray(Image.open(f).convert('RGB'), dtype=np.float32)
        h, w = a.shape[:2]; m = np.ones((h, w, 1), dtype=np.float32)
        if rampa:
            m[:, :rampa, 0] *= np.linspace(0, 1, rampa)[None, :]
        o = bas.copy(); r = o[y:y + h, x:x + w]
        r[..., :3] = np.clip(r[..., :3] + a * m * (r[..., 3:] > 200), 0, 255)
        # El borde del cuadro se mantiene encima del retrato.
        salida.append(Image.fromarray(o.astype(np.uint8), 'RGBA'))
    return salida


def guardar(ims, nombre):
    p = REPO / 'img' / f'{nombre}.webp'
    ims[0].save(p, save_all=True, append_images=ims[1:], duration=83, loop=0, quality=Q, method=METODO, alpha_quality=100)
    q = REPO / 'img' / f'{nombre}-quieto.webp'
    ims[0].save(q, quality=88, method=6)
    print(nombre, len(ims), 'cuadros', p.stat().st_size // 1024, 'KB · quieto', q.stat().st_size // 1024, 'KB')


def main():
    esc, mov = sys.argv[1], sys.argv[2]
    with tempfile.TemporaryDirectory() as t:
        txt = f"""<text class="n" font-size="168" x="82" y="232" letter-spacing="-4">{NOMBRE[0]}</text>
<text class="n" font-size="168" x="82" y="392" letter-spacing="-4">{NOMBRE[1]}</text>
<text class="t" font-size="40" x="88" y="496">{TITULAR}</text>
<text class="c" font-size="32" x="88" y="564">{LINEAS[0]}</text>
<text class="c" font-size="32" x="88" y="608">{LINEAS[1]}</text>"""
        guardar(componer(base(1700, 720, txt, t, 'e'), esc, 924, 0, 70), 'hero')
        txt = f"""<text class="n" font-size="100" x="48" y="668" letter-spacing="-2.5">{NOMBRE[0]} {NOMBRE[1]}</text>
<text class="t" font-size="33" x="50" y="736">{TITULAR}</text>
<text class="c" font-size="28" x="50" y="796">{LINEAS[0]}</text>
<text class="c" font-size="28" x="50" y="836">{LINEAS[1]}</text>"""
        guardar(componer(base(800, 880, txt, t, 'm'), mov, 0, 0, 0), 'hero-movil')


main()
