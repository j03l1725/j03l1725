#!/usr/bin/env python3
"""Genera img/terminal-dark.svg e img/terminal-light.svg.

Junta el retrato ASCII (assets/ascii_portrait.txt) con el panel de informacion
(data/profile.json) dentro de una ventana de terminal, y le mete la animacion de
tecleo con CSS. Lo corre el workflow diario para refrescar los contadores.

Restricciones que manda GitHub: el SVG viaja por su proxy de imagenes y se
renderiza como <img>, asi que NO hay JavaScript ni fuentes externas. Solo CSS y
fuentes del sistema.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parent.parent

# Metricas de la grilla monoespaciada. Courier New y los monospace de fallback
# avanzan 0.6 em por caracter: de ahi salen todas las posiciones.
ADVANCE = 0.6
ASCII_FS = 13.0
ASCII_LH = 15.6
PANEL_FS = 15.0
PANEL_LH = 21.5

PAD = 28.0
TITLEBAR = 36.0
GAP = 34.0

# Ritmo del tecleo.
ASCII_STEP = 0.045
PANEL_START = 0.35
PANEL_STEP = 0.085
TYPE_DUR = 0.28

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "chrome": "#161b22",
        "border": "#30363d",
        "title": "#8b949e",
        "ascii_from": "#58a6ff",
        "ascii_to": "#7ee787",
        "name": "#e6edf3",
        "label": "#58a6ff",
        "value": "#c9d1d9",
        "rule": "#7ee787",
        "dots": "#484f58",
        "accent": "#f2cc60",
        "muted": "#6e7681",
        "cursor": "#7ee787",
    },
    "light": {
        "bg": "#ffffff",
        "chrome": "#f6f8fa",
        "border": "#d0d7de",
        "title": "#57606a",
        "ascii_from": "#0550ae",
        "ascii_to": "#116329",
        "name": "#1f2328",
        "label": "#0969da",
        "value": "#24292f",
        "rule": "#1a7f37",
        "dots": "#afb8c1",
        "accent": "#9a6700",
        "muted": "#6e7781",
        "cursor": "#1a7f37",
    },
}


def human_span(start: date, today: date) -> str:
    """'2 años, 3 meses' — sin numeros de GitHub, solo tiempo de trayectoria."""
    months = (today.year - start.year) * 12 + (today.month - start.month)
    if today.day < start.day:
        months -= 1
    months = max(0, months)
    years, rest = divmod(months, 12)
    parts = []
    if years:
        parts.append(f"{years} año" + ("s" if years != 1 else ""))
    if rest or not years:
        parts.append(f"{rest} mes" + ("es" if rest != 1 else ""))
    return ", ".join(parts)


def build_lines(profile: dict, today: date) -> tuple[list[dict], int]:
    """Aplana los bloques de profile.json en lineas con segmentos coloreados."""
    spans = {
        "leading_teams": human_span(date.fromisoformat(profile["milestones"]["leading_teams_since"]), today),
        "cto": human_span(date.fromisoformat(profile["milestones"]["cto_since"]), today),
    }

    def fill(text: str) -> str:
        for key, value in spans.items():
            text = text.replace("{{" + key + "}}", value)
        return text

    items = [(label, fill(value)) for b in profile["blocks"] if b["type"] == "kv" for label, value in b["items"]]
    # El ancho del panel lo manda el par label+value mas largo: asi los puntos
    # suspensivos siempre alinean los valores contra el borde derecho.
    cols = max(len(label) + len(value) + 6 for label, value in items)
    cols = max(cols, len(f"{profile['user']}@{profile['host']}") + 12)

    lines: list[dict] = []
    for block in profile["blocks"]:
        if block["type"] == "head":
            prompt = f"{profile['user']}@{profile['host']}"
            lines.append({"segs": [(prompt, "rule"), ("  " + fill(block["text"]), "name")]})
            lines.append({"segs": [("─" * cols, "dots")]})
        elif block["type"] == "rule":
            title = f"─ {block['text']} "
            lines.append({"segs": [(title + "─" * max(0, cols - len(title)), "rule")]})
        elif block["type"] == "kv":
            for label, value in block["items"]:
                value = fill(value)
                dots = "." * max(2, cols - len(label) - len(value) - 3)
                lines.append(
                    {
                        "segs": [
                            (f"{label} ", "label"),
                            (dots, "dots"),
                            (f" {value}", "value"),
                        ]
                    }
                )
        if block["type"] in ("kv", "head"):
            lines.append({"segs": []})

    lines.append(
        {
            "segs": [(f"last updated: {today.isoformat()} ", "muted")],
            "cursor": True,
        }
    )
    return lines, cols


def render(profile: dict, ascii_art: list[str], theme_name: str, today: date) -> str:
    c = THEMES[theme_name]
    lines, cols = build_lines(profile, today)

    ascii_w = max(len(line) for line in ascii_art) * ASCII_FS * ADVANCE
    ascii_h = len(ascii_art) * ASCII_LH
    panel_w = cols * PANEL_FS * ADVANCE
    panel_h = len(lines) * PANEL_LH

    width = PAD * 2 + ascii_w + GAP + panel_w
    height = TITLEBAR + PAD + max(ascii_h, panel_h) + PAD

    ascii_x = PAD
    ascii_y = TITLEBAR + PAD + (max(ascii_h, panel_h) - ascii_h) / 2 + ASCII_FS
    panel_x = PAD + ascii_w + GAP
    panel_y = TITLEBAR + PAD + (max(ascii_h, panel_h) - panel_h) / 2 + PANEL_FS

    out: list[str] = []
    add = out.append
    add(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" role="img" '
        f'aria-label="Terminal con el retrato ASCII y el perfil de {escape(profile["user"])}@{escape(profile["host"])}">'
    )

    # --- estilos y animacion -------------------------------------------------
    css = [
        f'.t{{font-family:"Courier New",Courier,ui-monospace,monospace;white-space:pre}}',
        f".a{{font-size:{ASCII_FS}px;fill:url(#g)}}",
        f".p{{font-size:{PANEL_FS}px}}",
        f".title{{font-size:12px;fill:{c['title']}}}",
        f".label{{fill:{c['label']};font-weight:bold}}",
        f".value{{fill:{c['value']}}}",
        f".name{{fill:{c['name']};font-weight:bold}}",
        f".rule{{fill:{c['rule']};font-weight:bold}}",
        f".dots{{fill:{c['dots']}}}",
        f".muted{{fill:{c['muted']}}}",
        # El tecleo: cada linea vive dentro de un clip cuyo rectangulo crece de
        # izquierda a derecha. scaleX se anima en la GPU y no depende de que el
        # motor soporte animar el atributo width.
        #
        # El estado base es la linea COMPLETA y la animacion entra con
        # fill-mode:backwards (oculta la linea solo durante su retardo). Con
        # forwards + steps(), al terminar la animacion el motor deja el clip en
        # el ultimo escalon (23/24) y recorta para siempre los ultimos
        # caracteres de la linea.
        ".typer{transform:scaleX(1);transform-box:fill-box;transform-origin:left center;"
        f"animation:type {TYPE_DUR}s steps(24,end) backwards}}",
        "@keyframes type{from{transform:scaleX(0)}to{transform:scaleX(1)}}",
        f".cursor{{fill:{c['cursor']};opacity:0;animation:blink 1.06s step-end infinite backwards}}",
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}",
        # Sin animacion para quien la desactiva en el sistema.
        "@media (prefers-reduced-motion:reduce){.typer{animation:none}"
        ".cursor{animation:none;opacity:1}}",
    ]
    add(f"<style>{''.join(css)}</style>")
    add(
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="0.6" y2="1">'
        f'<stop offset="0%" stop-color="{c["ascii_from"]}"/>'
        f'<stop offset="100%" stop-color="{c["ascii_to"]}"/>'
        f"</linearGradient></defs>"
    )

    # --- ventana -------------------------------------------------------------
    add(
        f'<rect x="0.5" y="0.5" width="{width - 1:.0f}" height="{height - 1:.0f}" rx="10" '
        f'fill="{c["bg"]}" stroke="{c["border"]}"/>'
    )
    add(
        f'<path d="M0.5 10.5a10 10 0 0 1 10-10h{width - 21:.0f}a10 10 0 0 1 10 10v{TITLEBAR - 10:.0f}H0.5z" '
        f'fill="{c["chrome"]}" stroke="{c["border"]}"/>'
    )
    for i, dot in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        add(f'<circle cx="{22 + i * 18}" cy="{TITLEBAR / 2:.0f}" r="6" fill="{dot}"/>')
    add(
        f'<text class="t title" x="{width / 2:.0f}" y="{TITLEBAR / 2 + 4:.0f}" text-anchor="middle">'
        f'{escape(profile["title"])}</text>'
    )

    # --- retrato ASCII -------------------------------------------------------
    clip_id = 0
    for i, line in enumerate(ascii_art):
        if not line.strip():
            continue
        clip_id += 1
        y = ascii_y + i * ASCII_LH
        # El texto se dibuja sobre su linea base, asi que la caja del clip va de
        # la altura de mayusculas al descendente; si se cuelga de la linea base
        # hacia arriba, corta la mitad inferior de cada letra.
        w = len(line) * ASCII_FS * ADVANCE
        delay = i * ASCII_STEP
        add(
            f'<clipPath id="c{clip_id}"><rect class="typer" style="animation-delay:{delay:.2f}s" '
            f'x="{ascii_x:.1f}" y="{y - ASCII_FS:.1f}" width="{w + 2:.1f}" height="{ASCII_LH:.1f}"/></clipPath>'
        )
        # textLength fija el ancho de la linea a la grilla: sin esto, el visitante
        # que no tenga Courier New renderiza con otras metricas y la ultima palabra
        # de cada linea se sale del recorte.
        add(
            f'<text class="t a" x="{ascii_x:.1f}" y="{y:.1f}" clip-path="url(#c{clip_id})" '
            f'textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs" '
            f'xml:space="preserve">{escape(line)}</text>'
        )

    # --- panel ---------------------------------------------------------------
    for i, line in enumerate(lines):
        if not line["segs"]:
            continue
        clip_id += 1
        y = panel_y + i * PANEL_LH
        chars = sum(len(text) for text, _ in line["segs"])
        w = chars * PANEL_FS * ADVANCE
        delay = PANEL_START + i * PANEL_STEP
        add(
            f'<clipPath id="c{clip_id}"><rect class="typer" style="animation-delay:{delay:.2f}s" '
            f'x="{panel_x:.1f}" y="{y - PANEL_FS:.1f}" width="{w + 2:.1f}" height="{PANEL_LH:.1f}"/></clipPath>'
        )
        tspans = "".join(f'<tspan class="{cls}">{escape(text)}</tspan>' for text, cls in line["segs"])
        add(
            f'<text class="t p" x="{panel_x:.1f}" y="{y:.1f}" clip-path="url(#c{clip_id})" '
            f'textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs" '
            f'xml:space="preserve">{tspans}</text>'
        )
        if line.get("cursor"):
            # El cursor arranca cuando termina de escribirse su linea y ya no para:
            # es lo que mantiene el perfil vivo aunque la animacion haya terminado.
            cx = panel_x + w
            add(
                f'<rect class="cursor" x="{cx:.1f}" y="{y - PANEL_FS * 0.75:.1f}" '
                f'width="{PANEL_FS * ADVANCE:.1f}" height="{PANEL_FS:.1f}" '
                f'style="animation-delay:{delay + TYPE_DUR:.2f}s"/>'
            )

    add("</svg>")
    return "".join(out)


def main() -> None:
    profile = json.loads((REPO / "data" / "profile.json").read_text(encoding="utf-8"))
    ascii_art = (REPO / "assets" / "ascii_portrait.txt").read_text(encoding="utf-8").split("\n")
    while ascii_art and not ascii_art[-1].strip():
        ascii_art.pop()

    today = date.today()
    (REPO / "img").mkdir(exist_ok=True)
    for theme in THEMES:
        path = REPO / "img" / f"terminal-{theme}.svg"
        path.write_text(render(profile, ascii_art, theme, today), encoding="utf-8")
        print(f"escrito {path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
