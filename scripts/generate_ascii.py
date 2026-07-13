#!/usr/bin/env python3
"""Convierte assets/avatar.png en el retrato ASCII de assets/ascii_portrait.txt.

Se corre a mano (no en CI): el resultado se versiona para que el build del SVG
sea determinista y el ASCII se pueda retocar a mano linea por linea.

    python3 scripts/generate_ascii.py --cols 46 --ramp classic -o assets/ascii_portrait.txt

Espera una imagen con canal alfa (fondo ya removido con rembg). Si la imagen no
tiene alfa se usa tal cual y el fondo va a ensuciar el retrato.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps

REPO = Path(__file__).resolve().parent.parent

# De mas oscuro a mas claro. El SVG dibuja texto claro sobre fondo oscuro, asi que
# la rampa se invierte al mapear: mucha luz -> caracter denso.
RAMPS = {
    "classic": "@%#*+=-:. ",
    "dense": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "blocks": "█▓▒░ ",
    "soft": "@#8&o:*. ",
}

# El caracter monoespaciado es ~2x mas alto que ancho.
CHAR_ASPECT = 0.5


def stretch_inside_mask(gray: Image.Image, alpha: Image.Image, low: float, high: float) -> Image.Image:
    """Estira el histograma usando SOLO los pixeles de la persona.

    Si se estira contra la imagen completa, el fondo transparente (negro) domina
    el histograma y el retrato sale lavado, todo en tonos medios.
    """
    values = sorted(v for v, a in zip(gray.getdata(), alpha.getdata()) if a > 96)
    if not values:
        return gray
    lo = values[int(len(values) * low)]
    hi = values[min(len(values) - 1, int(len(values) * high))]
    if hi <= lo:
        return gray
    scale = 255.0 / (hi - lo)
    return gray.point(lambda v: max(0, min(255, int((v - lo) * scale))))


def local_contrast(gray: Image.Image, strength: float) -> Image.Image:
    """Realce high-pass: resta la iluminacion de fondo y deja los rasgos.

    La foto tiene luz muy plana, asi que a nivel global la cara cae toda en el
    mismo tono medio y en ASCII se vuelve una mancha. Restando una version
    borrosa se recupera el detalle local (ojos, cejas, nariz, mandibula).
    """
    if strength <= 0:
        return gray
    blur = gray.filter(ImageFilter.GaussianBlur(radius=max(2, gray.width / 12)))
    # gray - blur + 128, en el espacio de 8 bits
    high = ImageChops.add(ImageChops.subtract(gray, blur, scale=1, offset=128), Image.new("L", gray.size, 0))
    return Image.blend(gray, high, strength)


def render(
    img: Image.Image,
    cols: int,
    ramp: str,
    contrast: float,
    gamma: float,
    head: float = 1.0,
    equalize: bool = False,
    local: float = 0.0,
    sharpen: bool = False,
    invert: bool = False,
    edges: float = 0.0,
) -> str:
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    bbox = img.split()[3].getbbox()
    if bbox:
        img = img.crop(bbox)

    # head < 1 recorta a cabeza y hombros: si entra el torso completo, la cara
    # se queda con muy pocas filas y no se reconoce nadie.
    if head < 1.0:
        img = img.crop((0, 0, img.width, int(img.height * head)))
        bbox = img.split()[3].getbbox()
        if bbox:
            img = img.crop(bbox)

    # El realce se hace a resolucion completa y recien despues se reduce a la
    # grilla de caracteres: al reves, no queda detalle que realzar.
    full_gray = img.convert("L")
    if sharpen:
        full_gray = full_gray.filter(ImageFilter.UnsharpMask(radius=4, percent=140, threshold=2))
    full_gray = local_contrast(full_gray, local)
    if edges > 0:
        # Los contornos (ojos, cejas, nariz, mandibula) se oscurecen para que
        # caigan en caracteres densos y el retrato se lea como un trazo.
        contour = full_gray.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1))
        full_gray = ImageChops.subtract(full_gray, contour.point(lambda v: int(v * edges)))

    rows = max(1, round(cols * CHAR_ASPECT * img.height / img.width))
    alpha = img.split()[3].resize((cols, rows), Image.LANCZOS)
    gray = full_gray.resize((cols, rows), Image.LANCZOS)

    gray = stretch_inside_mask(gray, alpha, 0.02, 0.98)
    if equalize:
        gray = ImageOps.equalize(gray, mask=alpha.point(lambda a: 255 if a > 96 else 0))
    gray = ImageEnhance.Contrast(gray).enhance(contrast)

    chars = RAMPS[ramp]
    # La densidad del caracter funciona como tinta, no como luz: lo oscuro de la
    # foto (pelo, cejas, ojos, sombras) va a caracter denso y la piel a caracter
    # ralo. Al reves el pelo se vuelve un hueco vacio y la cabeza desaparece
    # contra el fondo del terminal.
    def level(v: int) -> float:
        t = v / 255 if not invert else (255 - v) / 255
        return t**gamma

    lut = [chars[min(len(chars) - 1, int(level(v) * len(chars)))] for v in range(256)]

    lines = []
    for y in range(rows):
        line = []
        for x in range(cols):
            # Fuera de la silueta no se dibuja nada: el retrato flota.
            line.append(lut[gray.getpixel((x, y))] if alpha.getpixel((x, y)) > 96 else " ")
        lines.append("".join(line).rstrip())
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("-i", "--input", default=str(REPO / "assets" / "avatar-cutout.png"))
    p.add_argument("-o", "--output", default=str(REPO / "assets" / "ascii_portrait.txt"))
    p.add_argument("--cols", type=int, default=46)
    p.add_argument("--ramp", choices=sorted(RAMPS), default="classic")
    p.add_argument("--contrast", type=float, default=1.35)
    p.add_argument("--gamma", type=float, default=1.0, help=">1 aclara, <1 oscurece")
    p.add_argument("--head", type=float, default=0.62, help="fraccion superior a conservar (cabeza y hombros)")
    p.add_argument("--equalize", action="store_true", help="ecualiza el histograma dentro de la silueta")
    p.add_argument("--local", type=float, default=0.55, help="realce de contraste local 0..1")
    p.add_argument("--sharpen", action="store_true", help="unsharp mask antes de reducir")
    p.add_argument("--invert", action="store_true", help="claro -> denso (tipo foto en vez de tinta)")
    p.add_argument("--edges", type=float, default=0.0, help="fuerza del trazo de contornos 0..1")
    p.add_argument("--print", action="store_true", help="imprime en vez de escribir el archivo")
    args = p.parse_args()

    art = render(
        Image.open(args.input),
        args.cols,
        args.ramp,
        args.contrast,
        args.gamma,
        args.head,
        args.equalize,
        args.local,
        args.sharpen,
        args.invert,
        args.edges,
    )
    if args.print:
        print(art)
    else:
        Path(args.output).write_text(art + "\n", encoding="utf-8")
        print(f"escrito {args.output} ({len(art.splitlines())} lineas)")


if __name__ == "__main__":
    main()
